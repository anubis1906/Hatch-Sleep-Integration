"""The Hatch Sleep integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant

from .api import HatchBleDevice
from .coordinator import HatchDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.NUMBER,
]


@dataclass
class HatchRuntimeData:
    """Runtime data attached to a config entry."""

    device: HatchBleDevice
    coordinator: HatchDataUpdateCoordinator


if TYPE_CHECKING:
    # ConfigEntry only became Generic in newer Home Assistant releases; guard the
    # subscript so this module still imports cleanly on older cores at runtime.
    HatchConfigEntry = ConfigEntry[HatchRuntimeData]
else:
    HatchConfigEntry = ConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: HatchConfigEntry) -> bool:
    """Set up Hatch Sleep from a config entry."""
    address = entry.data[CONF_ADDRESS]
    device = HatchBleDevice(hass, address)
    coordinator = HatchDataUpdateCoordinator(hass, device)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = HatchRuntimeData(device=device, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: HatchConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
