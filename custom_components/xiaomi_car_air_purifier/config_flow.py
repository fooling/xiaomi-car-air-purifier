"""Config flow for Xiaomi Car Air Purifier."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class XiaomiCarAirPurifierConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Car Air Purifier."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info

        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovery_info.name or "Xiaomi Car Air Purifier",
                data={},
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self._discovery_info.name or "Xiaomi Car Air Purifier"
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step to pick discovered device."""
        if user_input is not None:
            address = user_input["device"]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()

            self._discovery_info = self._discovered_devices[address]

            return self.async_create_entry(
                title=self._discovery_info.name or address,
                data={},
            )

        current_addresses = self._async_current_ids()

        # Get all discovered Bluetooth devices
        discovered = async_discovered_service_info(self.hass, False)

        _LOGGER.debug(
            "Found %d total bluetooth devices during manual setup",
            len(list(discovered))
        )

        for discovery in discovered:
            if (
                discovery.address in current_addresses
                or discovery.address in self._discovered_devices
            ):
                continue

            # Check if this is a Xiaomi Car Air Purifier
            # Match device name patterns
            if discovery.name:
                name_upper = discovery.name.upper()
                _LOGGER.debug("Checking device: %s (%s)", discovery.name, discovery.address)

                # More flexible matching
                if any(pattern in name_upper for pattern in ["MI-CAR", "MICAR", "XIAOMI CAR"]):
                    _LOGGER.info(
                        "Found Xiaomi Car Air Purifier: %s (%s)",
                        discovery.name,
                        discovery.address
                    )
                    self._discovered_devices[discovery.address] = discovery

        if not self._discovered_devices:
            _LOGGER.warning("No Xiaomi Car Air Purifier devices found")
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("device"): vol.In(
                        {
                            address: f"{discovery.name} ({address})"
                            for address, discovery in self._discovered_devices.items()
                        }
                    )
                }
            ),
        )
