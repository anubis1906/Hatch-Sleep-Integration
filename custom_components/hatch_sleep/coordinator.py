"""Data update coordinator for the Hatch Sleep integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HatchBleDevice, HatchBleDeviceError
from .const import LOGGER, UPDATE_SECONDS


class HatchDataUpdateCoordinator(DataUpdateCoordinator[None]):
    """Polls a Hatch BLE device on an interval and after every command."""

    def __init__(self, hass: HomeAssistant, device: HatchBleDevice) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=f"{device.address} coordinator",
            update_interval=timedelta(seconds=UPDATE_SECONDS),
        )
        self.device = device

    async def _async_update_data(self) -> None:
        try:
            await self.device.async_update()
        except HatchBleDeviceError as err:
            raise UpdateFailed(str(err)) from err
