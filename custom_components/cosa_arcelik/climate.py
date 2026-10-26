"""COSA climate entity."""
from __future__ import annotations

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.exceptions import HomeAssistantError

from .api import CosaRejected

from .const import DOMAIN, CODE_TO_MODE, MODE_TO_CODE, FAN_SPEED, VERTICAL, HORIZONTAL

MODES = {
    "cool": HVACMode.COOL,
    "heat": HVACMode.HEAT,
    "dry": HVACMode.DRY,
    "fan_only": HVACMode.FAN_ONLY,
}
INV_MODES = {v: k for k, v in MODES.items()}
REV_FAN = {value: key for key, value in FAN_SPEED.items()}


async def async_setup_entry(hass, entry, async_add_entities):
    api, coordinator, device_id = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CosaClimate(api, coordinator, device_id, entry.title)])


class CosaClimate(CoordinatorEntity, ClimateEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.DRY, HVACMode.FAN_ONLY]
    _attr_fan_modes = list(FAN_SPEED)
    _attr_swing_modes = list(VERTICAL)
    _attr_swing_horizontal_modes = list(HORIZONTAL)
    _attr_min_temp = 16
    _attr_max_temp = 30
    _attr_target_temperature_step = 1

    def __init__(self, api, coordinator, device_id, title):
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self._attr_unique_id = f"cosa_{device_id}_climate"
        self._attr_device_info = {"identifiers": {(DOMAIN, device_id)}, "name": title, "manufacturer": "Arçelik", "model": "12556 / COSA"}

    @property
    def _data(self):
        return self.coordinator.data or {}

    @property
    def supported_features(self):
        features = ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.SWING_MODE | ClimateEntityFeature.SWING_HORIZONTAL_MODE | ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF
        if self._data.get("acMode") in (0, 4):
            features |= ClimateEntityFeature.TARGET_TEMPERATURE
        return features

    @property
    def hvac_mode(self):
        if self._data.get("acPower") == 0:
            return HVACMode.OFF
        name = CODE_TO_MODE.get(self._data.get("acMode"))
        return MODES.get(name)

    @property
    def current_temperature(self):
        return self._data.get("temperature")

    @property
    def target_temperature(self):
        if self._data.get("acMode") in (1, 2):
            return 25
        return self._data.get("targetTemperature")

    @property
    def fan_mode(self):
        return REV_FAN.get(self._data.get("acFanSpeed"))

    @property
    def swing_mode(self):
        raw = self._data.get("acVerticalSwing")
        return next((label for label, code in VERTICAL.items() if code == raw), None)

    @property
    def swing_horizontal_mode(self):
        raw = self._data.get("acHorizontalSwing")
        return next((label for label, code in HORIZONTAL.items() if code == raw), None)

    async def async_set_swing_mode(self, swing_mode):
        if swing_mode not in VERTICAL:
            raise HomeAssistantError("Bilinmeyen dikey kanat pozisyonu")
        await self._send("acVerticalSwing", VERTICAL[swing_mode])

    async def async_set_swing_horizontal_mode(self, swing_horizontal_mode):
        if swing_horizontal_mode not in HORIZONTAL:
            raise HomeAssistantError("Bilinmeyen yatay kanat pozisyonu")
        await self._send("acHorizontalSwing", HORIZONTAL[swing_horizontal_mode])

    async def _send(self, key, value, *, extra=None):
        # Update Home Assistant immediately after COSA acknowledges the command.
        await self.api.command(self.device_id, key, value)
        state = {**self._data, key: value}
        if extra:
            state.update(extra)
        self.coordinator.async_set_updated_data(state)
        # Immediately read back the real device state, without waiting 30 s.
        # COSA sometimes rejects the read just after a mode transition;
        # retain the acknowledged optimistic state in that case.
        try:
            confirmed = await self.api.status(self.device_id)
        except HomeAssistantError:
            return
        if all(confirmed.get(field) == expected for field, expected in state.items()
               if field == key or (extra and field in extra)):
            self.coordinator.async_set_updated_data(confirmed)

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVACMode.OFF:
            await self._send("acPower", 0)
            return
        name = INV_MODES.get(hvac_mode)
        if name is None:
            raise HomeAssistantError("Desteklenmeyen çalışma modu")
        # Observed COSA behavior: mode selection turns the AC on.
        # Do not send a redundant power command based on stale state.
        await self._send("acMode", MODE_TO_CODE[name], extra={"acPower": 1})

    async def async_turn_on(self):
        await self._send("acPower", 1)

    async def async_turn_off(self):
        await self._send("acPower", 0)

    async def async_set_temperature(self, **kwargs):
        if self._data.get("acMode") not in (0, 4):
            raise HomeAssistantError("Nem alma ve fan modunda sıcaklık 25 °C sabittir")
        value = kwargs.get("temperature")
        if value is None or not 16 <= value <= 30:
            raise HomeAssistantError("Geçersiz hedef sıcaklık")
        await self._send("targetTemperature", value)

    async def async_set_fan_mode(self, fan_mode):
        if fan_mode not in FAN_SPEED:
            raise HomeAssistantError("Geçersiz fan hızı")
        await self._send("acFanSpeed", FAN_SPEED[fan_mode])
