"""Base entity for the Hatch Sleep integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import HatchDataUpdateCoordinator


class HatchSleepEntity(CoordinatorEntity[HatchDataUpdateCoordinator]):
    """Base entity tying a platform entity to a Hatch BLE device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HatchDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self.device = coordinator.device
        name = self.device.address
        if coordinator.config_entry is not None:
            name = coordinator.config_entry.title or name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device.address)},
            name=name,
            manufacturer=MANUFACTURER,
        )
