"""Independent vertical and horizontal air vanes."""
from __future__ import annotations
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.exceptions import HomeAssistantError
from .const import DOMAIN, VERTICAL, HORIZONTAL


async def async_setup_entry(hass, entry, async_add_entities):
    api, coordinator, device_id = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        AtlasVane(api, coordinator, device_id, "Dikey kanat", "acVerticalSwing", VERTICAL),
        AtlasVane(api, coordinator, device_id, "Yatay kanat", "acHorizontalSwing", HORIZONTAL),
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
