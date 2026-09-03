"""Switch platform for the Hatch Sleep integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HatchConfigEntry
from .coordinator import HatchDataUpdateCoordinator
from .entity import HatchSleepEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HatchConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Hatch Sleep power switch."""
    async_add_entities([HatchSleepPowerSwitch(entry.runtime_data.coordinator)])


class HatchSleepPowerSwitch(HatchSleepEntity, SwitchEntity):
    """Master power switch for a Hatch device."""

    _attr_translation_key = "power"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: HatchDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.device.address}_power"

    @property
    def is_on(self) -> bool:
        return self.device.state.power

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.device.async_power_on()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.device.async_power_off()
        self.async_write_ha_state()
