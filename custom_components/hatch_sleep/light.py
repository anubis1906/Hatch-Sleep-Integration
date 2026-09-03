"""Light platform for the Hatch Sleep integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HatchConfigEntry
from .const import DEFAULT_ON_BRIGHTNESS
from .coordinator import HatchDataUpdateCoordinator
from .entity import HatchSleepEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HatchConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Hatch Sleep light."""
    async_add_entities([HatchSleepLight(entry.runtime_data.coordinator)])


class HatchSleepLight(HatchSleepEntity, LightEntity):
    """Represents the RGB nightlight of a Hatch device."""

    _attr_translation_key = "light"
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}

    def __init__(self, coordinator: HatchDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.device.address}_light"

    @property
    def is_on(self) -> bool:
        return self.device.state.brightness > 0

    @property
    def brightness(self) -> int:
        return self.device.state.brightness

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        return self.device.state.rgb_color

    async def async_turn_on(self, **kwargs: Any) -> None:
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        brightness = kwargs.get(ATTR_BRIGHTNESS)

        if rgb_color is not None:
            await self.device.async_set_color(*rgb_color, brightness=brightness)
        elif brightness is not None:
            await self.device.async_set_brightness(brightness)
        elif not self.is_on:
            await self.device.async_set_brightness(DEFAULT_ON_BRIGHTNESS)

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.device.async_set_brightness(0)
        self.async_write_ha_state()
