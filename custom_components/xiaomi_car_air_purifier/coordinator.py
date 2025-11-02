"""Data update coordinator for Xiaomi Car Air Purifier."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .ble_client import XiaomiCarAirPurifierBLEClient
from .const import (
    DOMAIN,
    UPDATE_INTERVAL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MAX_RETRIES,
    CONSECUTIVE_FAILURES_THRESHOLD,
)

_LOGGER = logging.getLogger(__name__)


class XiaomiCarAirPurifierCoordinator(DataUpdateCoordinator):
    """Coordinator for Xiaomi Car Air Purifier data updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        # Get scan interval from options or use default
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.entry = entry
        self._ble_device = bluetooth.async_ble_device_from_address(
            hass, entry.unique_id
        )
        self._client = XiaomiCarAirPurifierBLEClient(self._ble_device)
        self._consecutive_failures = 0
        self._last_successful_data: dict | None = None
        entry.async_on_unload(entry.add_update_listener(self._async_update_listener))

    async def _async_update_listener(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Handle options update."""
        # Update scan interval when options change
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self.update_interval = timedelta(seconds=scan_interval)

    async def _async_update_data(self) -> dict:
        """Fetch data from the device with retry logic and state persistence."""
        status = None

        # Try to get status with retries
        for attempt in range(MAX_RETRIES):
            try:
                # Ensure connection
                if not self._client.is_connected:
                    _LOGGER.debug("Not connected, attempting to connect (attempt %d/%d)", attempt + 1, MAX_RETRIES)
                    if not await self._client.connect():
                        if attempt < MAX_RETRIES - 1:
                            _LOGGER.warning("Connection failed, retrying in 1 second...")
                            await asyncio.sleep(1)
                            continue
                        else:
                            _LOGGER.error("Failed to connect after %d attempts", MAX_RETRIES)
                            break

                # Try to read status
                _LOGGER.debug("Reading status (attempt %d/%d)", attempt + 1, MAX_RETRIES)
                status = await self._client.get_status()

                if status is not None:
                    # Success! Reset failure counter and cache the data
                    self._consecutive_failures = 0
                    self._last_successful_data = status
                    _LOGGER.debug("Successfully read status")
                    return status
                else:
                    _LOGGER.warning("Failed to read status (attempt %d/%d)", attempt + 1, MAX_RETRIES)
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(1)
                        # Try to reconnect for next attempt
                        await self._client.disconnect()

            except Exception as err:
                _LOGGER.warning("Error reading status (attempt %d/%d): %s", attempt + 1, MAX_RETRIES, err)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(1)
                    # Try to reconnect for next attempt
                    try:
                        await self._client.disconnect()
                    except Exception:
                        pass

        # All retries failed
        self._consecutive_failures += 1
        _LOGGER.warning(
            "Failed to update after %d retries (consecutive failures: %d/%d)",
            MAX_RETRIES,
            self._consecutive_failures,
            CONSECUTIVE_FAILURES_THRESHOLD,
        )

        # Only mark as unavailable after multiple consecutive failures
        if self._consecutive_failures >= CONSECUTIVE_FAILURES_THRESHOLD:
            _LOGGER.error(
                "Device marked as unavailable after %d consecutive failures",
                self._consecutive_failures,
            )
            raise UpdateFailed(
                f"Failed to update device after {self._consecutive_failures} consecutive attempts"
            )

        # Return last successful data to maintain state
        if self._last_successful_data is not None:
            _LOGGER.info(
                "Returning cached data to maintain device state (failures: %d/%d)",
                self._consecutive_failures,
                CONSECUTIVE_FAILURES_THRESHOLD,
            )
            return self._last_successful_data

        # No cached data and failures haven't reached threshold
        raise UpdateFailed("No data available yet")

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        await self._client.disconnect()

    async def async_set_power(self, power: bool) -> None:
        """Set device power state with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                # Ensure connection
                if not self._client.is_connected:
                    _LOGGER.debug("Not connected, attempting to connect before setting power")
                    if not await self._client.connect():
                        if attempt < MAX_RETRIES - 1:
                            _LOGGER.warning("Connection failed, retrying in 1 second...")
                            await asyncio.sleep(1)
                            continue
                        else:
                            _LOGGER.error("Failed to connect to set power after %d attempts", MAX_RETRIES)
                            return

                # Try to set power
                if await self._client.set_power(power):
                    _LOGGER.info("Successfully set power to %s", "ON" if power else "OFF")
                    await self.async_request_refresh()
                    return
                else:
                    _LOGGER.warning("Failed to set power (attempt %d/%d)", attempt + 1, MAX_RETRIES)
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(1)
                        # Try to reconnect for next attempt
                        await self._client.disconnect()

            except Exception as err:
                _LOGGER.warning("Error setting power (attempt %d/%d): %s", attempt + 1, MAX_RETRIES, err)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(1)
                    try:
                        await self._client.disconnect()
                    except Exception:
                        pass

        _LOGGER.error("Failed to set power after %d attempts", MAX_RETRIES)

    async def async_set_mode(self, mode: str) -> None:
        """Set device mode by name (Auto, Silent, Standard, Strong) with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                # Ensure connection
                if not self._client.is_connected:
                    _LOGGER.debug("Not connected, attempting to connect before setting mode")
                    if not await self._client.connect():
                        if attempt < MAX_RETRIES - 1:
                            _LOGGER.warning("Connection failed, retrying in 1 second...")
                            await asyncio.sleep(1)
                            continue
                        else:
                            _LOGGER.error("Failed to connect to set mode after %d attempts", MAX_RETRIES)
                            return

                # Try to set mode
                if await self._client.set_mode(mode):
                    _LOGGER.info("Successfully set mode to %s", mode)
                    await self.async_request_refresh()
                    return
                else:
                    _LOGGER.warning("Failed to set mode (attempt %d/%d)", attempt + 1, MAX_RETRIES)
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(1)
                        # Try to reconnect for next attempt
                        await self._client.disconnect()

            except Exception as err:
                _LOGGER.warning("Error setting mode (attempt %d/%d): %s", attempt + 1, MAX_RETRIES, err)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(1)
                    try:
                        await self._client.disconnect()
                    except Exception:
                        pass

        _LOGGER.error("Failed to set mode after %d attempts", MAX_RETRIES)

