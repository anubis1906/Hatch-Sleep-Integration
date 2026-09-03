"""Select platform for the Hatch Sleep integration."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HatchConfigEntry
from .const import SOUND_NAME_TO_VALUE, SOUND_VALUE_TO_NAME
from .coordinator import HatchDataUpdateCoordinator
from .entity import HatchSleepEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HatchConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Hatch Sleep sound select entity."""
    async_add_entities([HatchSleepSoundSelect(entry.runtime_data.coordinator)])


class HatchSleepSoundSelect(HatchSleepEntity, SelectEntity):
    """Selects which sound the Hatch device is playing."""

    _attr_translation_key = "sound"
    _attr_options = list(SOUND_NAME_TO_VALUE)

    def __init__(self, coordinator: HatchDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.device.address}_sound"

    @property
    def current_option(self) -> str | None:
        return SOUND_VALUE_TO_NAME.get(self.device.state.sound)

    async def async_select_option(self, option: str) -> None:
        await self.device.async_set_sound(SOUND_NAME_TO_VALUE[option])
        self.async_write_ha_state()
