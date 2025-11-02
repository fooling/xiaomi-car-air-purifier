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

from .const import DOMAIN, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class XiaomiCarAirPurifierConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Car Air Purifier."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return XiaomiCarAirPurifierOptionsFlow(config_entry)

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
        errors = {}

        if user_input is not None:
            address = user_input["device"]

            # If manual input, validate MAC address format
            if address not in self._discovered_devices:
                address = address.strip().upper()

                # Validate MAC address format
                import re
                if not re.match(r'^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$', address):
                    errors["device"] = "invalid_mac"
                else:
                    # Normalize MAC address format
                    address = address.replace("-", ":")

            if not errors:
                await self.async_set_unique_id(address, raise_on_progress=False)
                self._abort_if_unique_id_configured()

                # Try to get device info from discovered devices
                if address in self._discovered_devices:
                    self._discovery_info = self._discovered_devices[address]
                    title = self._discovery_info.name or address
                else:
                    # Try to find in all discovered devices
                    discovered = async_discovered_service_info(self.hass)
                    for discovery in discovered:
                        if discovery.address.upper() == address:
                            self._discovery_info = discovery
                            title = discovery.name or address
                            break
                    else:
                        # Device not found, create entry anyway
                        title = f"Xiaomi Car Purifier ({address})"
                        _LOGGER.info("Creating entry for device not currently discovered: %s", address)

                return self.async_create_entry(
                    title=title,
                    data={},
                    options={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
                )

        current_addresses = self._async_current_ids()

        # Get all discovered Bluetooth devices
        discovered = async_discovered_service_info(self.hass)

        discovered_list = list(discovered)
        _LOGGER.info(
            "Found %d total bluetooth devices during manual setup",
            len(discovered_list)
        )

        # Log all discovered devices for debugging
        for i, discovery in enumerate(discovered_list[:20], 1):  # Log first 20
            _LOGGER.info(
                "Bluetooth device #%d: name=%s, address=%s",
                i, discovery.name or "Unknown", discovery.address
            )

        for discovery in discovered_list:
            if (
                discovery.address in current_addresses
                or discovery.address in self._discovered_devices
            ):
                continue

            # Check if this is a Xiaomi Car Air Purifier
            # Match device name patterns
            if discovery.name:
                name_upper = discovery.name.upper()

                # More flexible matching - match any device with "MI" or "XIAOMI"
                if any(pattern in name_upper for pattern in [
                    "MI-CAR", "MICAR", "XIAOMI CAR", "MI CAR",
                    "XIAOMI-CAR", "XMCAR", "米家车载"
                ]):
                    _LOGGER.info(
                        "Found Xiaomi Car Air Purifier: %s (%s)",
                        discovery.name,
                        discovery.address
                    )
                    self._discovered_devices[discovery.address] = discovery

        # Build data schema based on discovered devices
        if self._discovered_devices:
            # Show dropdown with discovered devices
            device_options = {
                address: f"{discovery.name} ({address})"
                for address, discovery in self._discovered_devices.items()
            }
            data_schema = vol.Schema({
                vol.Required("device"): vol.In(device_options)
            })
        else:
            # Show text input for manual entry
            _LOGGER.warning("No Xiaomi Car Air Purifier devices found automatically")
            data_schema = vol.Schema({
                vol.Required("device"): str
            })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual device entry."""
        errors = {}

        if user_input is not None:
            address = user_input["address"].strip().upper()

            # Validate MAC address format
            import re
            if not re.match(r'^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$', address):
                errors["address"] = "invalid_mac"
            else:
                # Normalize MAC address format
                address = address.replace("-", ":")

                await self.async_set_unique_id(address, raise_on_progress=False)
                self._abort_if_unique_id_configured()

                # Try to find the device in discovered devices
                discovered = async_discovered_service_info(self.hass)
                for discovery in discovered:
                    if discovery.address.upper() == address:
                        self._discovery_info = discovery
                        return self.async_create_entry(
                            title=discovery.name or address,
                            data={},
                        )

                # Device not found in discovery, but create entry anyway
                # It may be powered off now but will connect later
                _LOGGER.info("Creating entry for device not currently discovered: %s", address)
                return self.async_create_entry(
                    title=f"Xiaomi Car Purifier ({address})",
                    data={},
                )

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required("address"): str,
                }
            ),
            errors=errors,
        )


class XiaomiCarAirPurifierOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Xiaomi Car Air Purifier."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current scan interval or use default
        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=current_scan_interval,
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=600))
                }
            ),
        )
