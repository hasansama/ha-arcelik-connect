"""Arçelik Connect (COSA) Home Assistant integration."""
from __future__ import annotations
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import HomeAssistantError

from .api import CosaApi, CosaRejected
from .const import DOMAIN, POLL_SECONDS

PLATFORMS = ["climate", "select"]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = CosaApi(async_get_clientsession(hass), entry.data["email"], entry.data["password"])
    device_id = entry.data["device_id"]

    consecutive_state_rejections = 0
    last_good_state = None

    async def async_update():
        nonlocal consecutive_state_rejections, last_good_state
        try:
            state = await api.status(device_id)
        except CosaRejected as exc:
            if exc.code == 100 and last_good_state is not None and consecutive_state_rejections < 2:
                consecutive_state_rejections += 1
                _LOGGER.warning(
                    "COSA %s durum sorgusu geçici olarak reddedildi (100); "
                    "son bilinen durum korunuyor (%d/2)",
                    entry.title,
                    consecutive_state_rejections,
                )
                return last_good_state
            raise UpdateFailed(str(exc)) from exc
        except HomeAssistantError as exc:
            raise UpdateFailed(str(exc)) from exc
        consecutive_state_rejections = 0
        last_good_state = state
        return state

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"COSA {entry.title}",
        update_method=async_update,
        update_interval=timedelta(seconds=POLL_SECONDS),
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = (api, coordinator, device_id)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if result:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return result
