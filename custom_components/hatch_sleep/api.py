"""BLE client for Hatch Rest / Rest Mini / Rest+ (1st-gen) devices."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import (
    CHAR_FEEDBACK,
    CHAR_TX,
    COMMAND_SETTLE_SECONDS,
    DEFAULT_ON_BRIGHTNESS,
    FEEDBACK_AUDIO_MARKER,
    FEEDBACK_AUDIO_MARKER_INDEX,
    FEEDBACK_BLUE_INDEX,
    FEEDBACK_BRIGHTNESS_INDEX,
    FEEDBACK_COLOR_MARKER,
    FEEDBACK_COLOR_MARKER_INDEX,
    FEEDBACK_GREEN_INDEX,
    FEEDBACK_MIN_LENGTH,
    FEEDBACK_POWER_MARKER,
    FEEDBACK_POWER_MARKER_INDEX,
    FEEDBACK_POWER_STATE_INDEX,
    FEEDBACK_POWER_STATE_MASK,
    FEEDBACK_RED_INDEX,
    FEEDBACK_SOUND_INDEX,
    FEEDBACK_VOLUME_INDEX,
    LOGGER,
)


class HatchBleDeviceError(Exception):
    """Raised when the device cannot be reached or returns unexpected data."""


class HatchBleDeviceNotFound(HatchBleDeviceError):
    """Raised when the device is not currently visible to any bluetooth adapter."""


@dataclass
class HatchState:
    """Last known state of a Hatch device."""

    power: bool = False
    red: int = 255
    green: int = 255
    blue: int = 255
    brightness: int = 0
    sound: int = 0
    volume: int = 0

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        return (self.red, self.green, self.blue)


class HatchBleDevice:
    """Wraps the Hatch BLE GATT protocol behind a small async API.

    The device exposes a single writable characteristic (CHAR_TX) that
    accepts short ASCII commands, and a single readable characteristic
    (CHAR_FEEDBACK) that reports the full current state. Every command
    below results in a fresh read of CHAR_FEEDBACK so local state always
    reflects what the device actually applied.
    """

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        self._hass = hass
        self.address = address
        self.state = HatchState()
        self._lock = asyncio.Lock()

    async def _connect(self) -> BleakClientWithServiceCache:
        ble_device = bluetooth.async_ble_device_from_address(
            self._hass, self.address, connectable=True
        )
        if ble_device is None:
            raise HatchBleDeviceNotFound(
                f"Hatch device {self.address} is not currently in bluetooth range"
            )
        try:
            return await establish_connection(
                BleakClientWithServiceCache, ble_device, ble_device.name or self.address
            )
        except (BleakError, TimeoutError, asyncio.TimeoutError) as err:
            raise HatchBleDeviceError(
                f"Could not connect to Hatch device {self.address}: {err}"
            ) from err

    def _parse_feedback(self, raw: bytes) -> HatchState:
        if len(raw) < FEEDBACK_MIN_LENGTH:
            raise HatchBleDeviceError(
                f"Unexpected feedback payload from {self.address}: {raw!r}"
            )
        if (
            raw[FEEDBACK_COLOR_MARKER_INDEX] != FEEDBACK_COLOR_MARKER
            or raw[FEEDBACK_AUDIO_MARKER_INDEX] != FEEDBACK_AUDIO_MARKER
            or raw[FEEDBACK_POWER_MARKER_INDEX] != FEEDBACK_POWER_MARKER
        ):
            raise HatchBleDeviceError(
                f"Unrecognized feedback payload from {self.address}: {raw!r}"
            )

        power = not bool(
            FEEDBACK_POWER_STATE_MASK & raw[FEEDBACK_POWER_STATE_INDEX]
        )

        return HatchState(
            power=power,
            red=raw[FEEDBACK_RED_INDEX],
            green=raw[FEEDBACK_GREEN_INDEX],
            blue=raw[FEEDBACK_BLUE_INDEX],
            brightness=raw[FEEDBACK_BRIGHTNESS_INDEX],
            sound=raw[FEEDBACK_SOUND_INDEX],
            volume=raw[FEEDBACK_VOLUME_INDEX],
        )

    async def _async_refresh_locked(self, client: BleakClientWithServiceCache) -> None:
        raw = await client.read_gatt_char(CHAR_FEEDBACK)
        self.state = self._parse_feedback(bytes(raw))

    async def async_update(self) -> None:
        """Connect and refresh the cached state from the device."""
        async with self._lock:
            client = await self._connect()
            try:
                await self._async_refresh_locked(client)
            except BleakError as err:
                raise HatchBleDeviceError(
                    f"Failed reading state from {self.address}: {err}"
                ) from err
            finally:
                await client.disconnect()

    async def _async_send_command(self, command: str) -> None:
        LOGGER.debug("Sending command %s to %s", command, self.address)
        async with self._lock:
            client = await self._connect()
            try:
                await client.write_gatt_char(
                    CHAR_TX, bytearray(command, "utf-8"), response=True
                )
                await asyncio.sleep(COMMAND_SETTLE_SECONDS)
                await self._async_refresh_locked(client)
            except BleakError as err:
                raise HatchBleDeviceError(
                    f"Failed sending command to {self.address}: {err}"
                ) from err
            finally:
                await client.disconnect()

    async def async_power_on(self) -> None:
        await self._async_send_command("SI{:02x}".format(1))

    async def async_power_off(self) -> None:
        await self._async_send_command("SI{:02x}".format(0))

    async def async_set_color(
        self, red: int, green: int, blue: int, brightness: int | None = None
    ) -> None:
        if brightness is None:
            brightness = self.state.brightness or DEFAULT_ON_BRIGHTNESS
        await self._async_send_command(
            "SC{:02x}{:02x}{:02x}{:02x}".format(red, green, blue, brightness)
        )

    async def async_set_brightness(self, brightness: int) -> None:
        red, green, blue = self.state.rgb_color
        await self._async_send_command(
            "SC{:02x}{:02x}{:02x}{:02x}".format(red, green, blue, brightness)
        )

    async def async_set_sound(self, sound: int) -> None:
        await self._async_send_command("SN{:02x}".format(sound))

    async def async_set_volume(self, volume: int) -> None:
        await self._async_send_command("SV{:02x}".format(volume))
