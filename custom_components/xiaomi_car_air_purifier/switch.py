"""Switch platform for Xiaomi Car Air Purifier."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import XiaomiCarAirPurifierCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch from a config entry."""
    coordinator: XiaomiCarAirPurifierCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([XiaomiPowerSwitch(coordinator, entry)])


class XiaomiPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of Xiaomi Car Air Purifier power switch."""

    def __init__(
        self,
        coordinator: XiaomiCarAirPurifierCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_power"
        self._attr_name = "Power"
        self._attr_icon = "mdi:power"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.unique_id)},
            "name": entry.title,
            "manufacturer": "Xiaomi",
            "model": "Car Air Purifier",
        }

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        if self.coordinator.data:
            return self.coordinator.data.get("power", False)
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.async_set_power(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.async_set_power(False)
