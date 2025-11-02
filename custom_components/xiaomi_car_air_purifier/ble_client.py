"""BLE Client for Xiaomi Car Air Purifier."""
from __future__ import annotations

import logging
from typing import Any

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import establish_connection

from .const import (
    MODE_CHAR_UUID,
    MODE_NAMES,
    MODE_VALUES,
    POWER_CHAR_UUID,
    POWER_OFF,
    POWER_ON,
)

_LOGGER = logging.getLogger(__name__)


class XiaomiCarAirPurifierBLEClient:
    """BLE client for Xiaomi Car Air Purifier."""

    def __init__(self, device: BLEDevice) -> None:
        """Initialize the BLE client."""
        self._device = device
        self._client: BleakClient | None = None

    async def connect(self) -> bool:
        """Connect to the device."""
        try:
            _LOGGER.debug("Connecting to %s", self._device.address)
            self._client = await establish_connection(
                BleakClient, self._device, self._device.address
            )
            _LOGGER.info("Connected to %s", self._device.address)
            return True
        except BleakError as err:
            _LOGGER.error("Failed to connect: %s", err)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        if self._client and self._client.is_connected:
            try:
                await self._client.disconnect()
                _LOGGER.info("Disconnected from %s", self._device.address)
            except BleakError as err:
                _LOGGER.error("Error during disconnect: %s", err)

    async def get_status(self) -> dict[str, Any] | None:
        """Get device status by reading characteristics."""
        if not self._client or not self._client.is_connected:
            _LOGGER.error("Not connected to device")
            return None

        try:
            # Read power state
            power_data = await self._client.read_gatt_char(POWER_CHAR_UUID)
            power = bool(power_data[0])

            # Read mode
            mode_data = await self._client.read_gatt_char(MODE_CHAR_UUID)
            mode_byte = mode_data[0]
            mode_name = MODE_NAMES.get(mode_byte, "Unknown")

            _LOGGER.debug(
                "Status read - Power: %s, Mode byte: 0x%02x (%s)",
                "ON" if power else "OFF",
                mode_byte,
                mode_name,
            )

            return {
                "power": power,
                "mode": mode_name,
                "mode_byte": mode_byte,
            }

        except BleakError as err:
            _LOGGER.error("Failed to read status: %s", err)
            return None

    async def set_power(self, power: bool) -> bool:
        """Turn device on or off."""
        if not self._client or not self._client.is_connected:
            _LOGGER.error("Not connected to device")
            return False

        try:
            data = POWER_ON if power else POWER_OFF
            _LOGGER.debug("Setting power: %s (0x%02x)", "ON" if power else "OFF", data[0])
            await self._client.write_gatt_char(POWER_CHAR_UUID, data)
            return True
        except BleakError as err:
            _LOGGER.error("Failed to set power: %s", err)
            return False

    async def set_mode(self, mode_name: str) -> bool:
        """Set device mode."""
        if not self._client or not self._client.is_connected:
            _LOGGER.error("Not connected to device")
            return False

        if mode_name not in MODE_VALUES:
            _LOGGER.error("Invalid mode: %s", mode_name)
            return False

        try:
            mode_data = MODE_VALUES[mode_name]
            _LOGGER.debug(
                "Setting mode: %s (%s)",
                mode_name,
                " ".join(f"0x{b:02x}" for b in mode_data),
            )
            await self._client.write_gatt_char(MODE_CHAR_UUID, mode_data)
            return True
        except BleakError as err:
            _LOGGER.error("Failed to set mode: %s", err)
            return False

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._client is not None and self._client.is_connected
