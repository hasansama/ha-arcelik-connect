"""Independent vertical and horizontal air vanes."""
from __future__ import annotations
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.exceptions import HomeAssistantError
from .const import DOMAIN, VERTICAL, HORIZONTAL, MODE_TO_CODE, CODE_TO_MODE


async def async_setup_entry(hass, entry, async_add_entities):
    api, coordinator, device_id = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        AtlasVane(api, coordinator, device_id, "Dikey kanat", "acVerticalSwing", VERTICAL),
        AtlasVane(api, coordinator, device_id, "Yatay kanat", "acHorizontalSwing", HORIZONTAL),
        AtlasOperatingMode(api, coordinator, device_id),
    ])


class AtlasVane(CoordinatorEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:air-filter"

    def __init__(self, api, coordinator, device_id, name, field, mapping):
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self.field = field
        self.mapping = mapping
        self._attr_name = name
        self._attr_options = list(mapping)
        self._attr_unique_id = f"cosa_{device_id}_{field}"
        self._attr_device_info = {"identifiers": {(DOMAIN, device_id)}}

    @property
    def current_option(self):
        current = (self.coordinator.data or {}).get(self.field)
        return next((label for label, code in self.mapping.items() if code == current), None)

    async def async_select_option(self, option):
        if option not in self.mapping:
            raise HomeAssistantError("Bilinmeyen kanat pozisyonu")
        await self.api.command(self.device_id, self.field, self.mapping[option])
        self.coordinator.async_set_updated_data({
            **(self.coordinator.data or {}),
            self.field: self.mapping[option],
        })
        try:
            confirmed = await self.api.status(self.device_id)
        except HomeAssistantError:
            return
        self.coordinator.async_set_updated_data(confirmed)


# Home Assistant's built-in HVACMode.DRY label is translated globally as
# "Kuru". Expose a localized select while retaining the standard climate mode.
DISPLAY_MODES = {
    "Kapalı": None,
    "Soğutma": "cool",
    "Isıtma": "heat",
    "Nem Alma": "dry",
    "Fan": "fan_only",
}


class AtlasOperatingMode(CoordinatorEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Çalışma modu"
    _attr_icon = "mdi:air-conditioner"
    _attr_options = list(DISPLAY_MODES)

    def __init__(self, api, coordinator, device_id):
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self._attr_unique_id = f"cosa_{device_id}_operation_mode_select"
        self._attr_device_info = {"identifiers": {(DOMAIN, device_id)}}

    @property
    def current_option(self):
        data = self.coordinator.data or {}
        if data.get("acPower") == 0:
            return "Kapalı"
        mode = CODE_TO_MODE.get(data.get("acMode"))
        return next((label for label, value in DISPLAY_MODES.items() if value == mode), None)

    async def async_select_option(self, option):
        if option not in DISPLAY_MODES:
            raise HomeAssistantError("Bilinmeyen çalışma modu")
        if option == "Kapalı":
            await self.api.command(self.device_id, "acPower", 0)
            local = {**(self.coordinator.data or {}), "acPower": 0}
        else:
            code = MODE_TO_CODE[DISPLAY_MODES[option]]
            await self.api.command(self.device_id, "acMode", code)
            local = {**(self.coordinator.data or {}), "acMode": code, "acPower": 1}
        self.coordinator.async_set_updated_data(local)
        try:
            confirmed = await self.api.status(self.device_id)
        except HomeAssistantError:
            return
        self.coordinator.async_set_updated_data(confirmed)
