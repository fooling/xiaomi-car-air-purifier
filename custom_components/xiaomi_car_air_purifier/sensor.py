"""Sensor platform for Xiaomi Car Air Purifier."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import XiaomiCarAirPurifierCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class XiaomiSensorEntityDescription(SensorEntityDescription):
    """Describes Xiaomi sensor entity."""

    value_fn: Callable[[dict], any] | None = None


SENSORS: tuple[XiaomiSensorEntityDescription, ...] = (
    XiaomiSensorEntityDescription(
        key="mode",
        name="Mode",
        icon="mdi:air-filter",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("mode", "Unknown"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: XiaomiCarAirPurifierCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        XiaomiSensorEntity(coordinator, entry, description) for description in SENSORS
    )


class XiaomiSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of a Xiaomi Car Air Purifier sensor."""

    entity_description: XiaomiSensorEntityDescription

    def __init__(
        self,
        coordinator: XiaomiCarAirPurifierCoordinator,
        entry: ConfigEntry,
        description: XiaomiSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.unique_id)},
            "name": entry.title,
            "manufacturer": "Xiaomi",
            "model": "Car Air Purifier",
        }

    @property
    def native_value(self) -> any:
        """Return the state of the sensor."""
        if self.coordinator.data and self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None
