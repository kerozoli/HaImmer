"""Binary sensor platform for the ImmerGas integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_KEY_BOILER,
    DATA_KEY_HEATING,
    DOMAIN,
    STABLE_KEY_TEMPERATURE,
    STABLE_KEY_THROTTLE,
)
from .coordinator import ImmerGasCoordinator

BINARY_SENSOR_DESCRIPTIONS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key=DATA_KEY_HEATING,
        name="ImmerGas Heating",
    ),
    BinarySensorEntityDescription(
        key=DATA_KEY_BOILER,
        name="ImmerGas Boiler",
    ),
    BinarySensorEntityDescription(
        key=STABLE_KEY_TEMPERATURE,
        name="ImmerGas Stable Temperaute",
    ),
    BinarySensorEntityDescription(
        key=STABLE_KEY_THROTTLE,
        name="ImmerGas Minimum Throttle",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ImmerGas binary sensors from a config entry."""
    coordinator: ImmerGasCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ImmerGasBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class ImmerGasBinarySensor(CoordinatorEntity[ImmerGasCoordinator], BinarySensorEntity):
    """Representation of an ImmerGas binary sensor."""

    entity_description: BinarySensorEntityDescription

    def __init__(
        self,
        coordinator: ImmerGasCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
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
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        return bool(value)
