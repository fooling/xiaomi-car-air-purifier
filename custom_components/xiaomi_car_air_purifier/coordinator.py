"""Data update coordinator for Xiaomi Car Air Purifier."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .ble_client import XiaomiCarAirPurifierBLEClient
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class XiaomiCarAirPurifierCoordinator(DataUpdateCoordinator):
    """Coordinator for Xiaomi Car Air Purifier data updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.entry = entry
        self._ble_device = bluetooth.async_ble_device_from_address(
            hass, entry.unique_id
        )
        self._client = XiaomiCarAirPurifierBLEClient(self._ble_device)

    async def _async_update_data(self) -> dict:
        """Fetch data from the device."""
        if not self._client.is_connected:
            if not await self._client.connect():
                raise UpdateFailed("Failed to connect to device")

        status = await self._client.get_status()
        if status is None:
            raise UpdateFailed("Failed to get device status")

        return status

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        await self._client.disconnect()

    async def async_set_power(self, power: bool) -> None:
        """Set device power state."""
        if await self._client.set_power(power):
            await self.async_request_refresh()

    async def async_set_mode(self, mode: str) -> None:
        """Set device mode by name (Auto, Silent, Standard, Strong)."""
        if await self._client.set_mode(mode):
            await self.async_request_refresh()

