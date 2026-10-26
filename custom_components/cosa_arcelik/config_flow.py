"""User interface setup for Arçelik Connect."""
from __future__ import annotations
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import HomeAssistantError

from .api import CosaApi
from .const import DOMAIN


class CosaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                api = CosaApi(async_get_clientsession(self.hass), user_input["email"], user_input["password"])
                endpoints = await api.devices()
                devices = [e for e in endpoints if e.get("id") is not None]
                if not devices:
                    errors["base"] = "no_devices"
                else:
                    self._credentials = user_input
                    self._choices = {str(e["id"]): e.get("name", "Klima") for e in devices}
                    return await self.async_step_select_device()
            except (HomeAssistantError, aiohttp.ClientError):
                errors["base"] = "cannot_connect"
        schema = vol.Schema({vol.Required("email"): str, vol.Required("password"): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_select_device(self, user_input=None):
        if user_input is not None:
            dev_id = user_input["device_id"]
            await self.async_set_unique_id(f"cosa_{dev_id}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=self._choices[dev_id], data={**self._credentials, "device_id": dev_id})
        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({vol.Required("device_id"): vol.In(self._choices)}),
        )
