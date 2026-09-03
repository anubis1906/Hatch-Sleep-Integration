"""Number platform for the Hatch Sleep integration."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HatchConfigEntry
from .const import MAX_VOLUME, MIN_VOLUME
from .coordinator import HatchDataUpdateCoordinator
from .entity import HatchSleepEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HatchConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Hatch Sleep volume number entity."""
    async_add_entities([HatchSleepVolumeNumber(entry.runtime_data.coordinator)])


class HatchSleepVolumeNumber(HatchSleepEntity, NumberEntity):
    """Controls the sound volume of a Hatch device."""

    _attr_translation_key = "volume"
    _attr_native_min_value = MIN_VOLUME
    _attr_native_max_value = MAX_VOLUME
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: HatchDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.device.address}_volume"

    @property
    def native_value(self) -> int:
        return self.device.state.volume

    async def async_set_native_value(self, value: float) -> None:
        await self.device.async_set_volume(int(value))
        self.async_write_ha_state()
