"""Fan platform for Xiaomi Car Air Purifier."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import XiaomiCarAirPurifierCoordinator

_LOGGER = logging.getLogger(__name__)

# Preset modes matching the device capabilities
PRESET_MODES = ["Auto", "Silent", "Standard", "Strong"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up fan from a config entry."""
    coordinator: XiaomiCarAirPurifierCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([XiaomiCarAirPurifierFan(coordinator, entry)])


class XiaomiCarAirPurifierFan(CoordinatorEntity, FanEntity):
    """Representation of Xiaomi Car Air Purifier as a fan entity."""

    _attr_supported_features = (
        FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )

    def __init__(
        self,
        coordinator: XiaomiCarAirPurifierCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the fan."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_fan"
        self._attr_name = "Fan"
        self._attr_preset_modes = PRESET_MODES
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.unique_id)},
            "name": entry.title,
            "manufacturer": "Xiaomi",
            "model": "Car Air Purifier",
        }

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        if self.coordinator.data:
            return self.coordinator.data.get("power", False)
        return False

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        if not self.coordinator.data:
            return None

        return self.coordinator.data.get("mode")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        if preset_mode in PRESET_MODES:
            await self.coordinator.async_set_mode(preset_mode)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        await self.coordinator.async_set_power(True)

        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        await self.coordinator.async_set_power(False)
