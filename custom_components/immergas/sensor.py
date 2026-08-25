"""Sensor platform for the ImmerGas integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_KEY_TEMPERATURE, DATA_KEY_THROTTLE, DOMAIN
from .coordinator import ImmerGasCoordinator

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=DATA_KEY_TEMPERATURE,
        name="ImmerGas Temperaute",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key=DATA_KEY_THROTTLE,
        name="ImmerGas Throttle",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ImmerGas sensors from a config entry."""
    coordinator: ImmerGasCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ImmerGasSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class ImmerGasSensor(CoordinatorEntity[ImmerGasCoordinator], SensorEntity):
    """Representation of an ImmerGas sensor."""

    entity_description: SensorEntityDescription

    def __init__(
        self, coordinator: ImmerGasCoordinator, description: SensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="ImmerGas",
            manufacturer="ImmerGas",
            model="ImmerGas REST Device",
        )

    @property
    def native_value(self) -> float | int | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self.entity_description.key)
