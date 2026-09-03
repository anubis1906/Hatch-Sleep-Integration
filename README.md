# Hatch Sleep Integration

A [Home Assistant](https://www.home-assistant.io/) custom integration that controls a
**Hatch Rest / Rest Mini / Rest+ (1st-generation)** sound machine and nightlight directly
over Bluetooth Low Energy (BLE) — no cloud account, hub, or internet connection required.

## Supported devices

This integration talks to the original BLE GATT protocol shared by the first generation
of Hatch Rest hardware (Hatch Rest, Rest Mini, Rest+ 1st-gen). It identifies devices by
the Bluetooth manufacturer ID Hatch's firmware advertises (`1076`).

It does **not** support newer Wi-Fi-connected devices (2nd-gen Rest+, Restore, Restore 2)
that rely on Hatch's cloud API — those use a completely different protocol.

## Features

Each paired device is exposed as one Home Assistant device with four entities:

| Entity | Platform | Description |
| --- | --- | --- |
| Power | `switch` | Master on/off for the whole device |
| Light | `light` | RGB color and brightness of the nightlight |
| Sound | `select` | Which sound is playing (or "None") |
| Volume | `number` | Sound volume (0-100) |

All entities poll the device every 60 seconds and immediately refresh after any command
you send, so Home Assistant's state always matches what's shown in the Hatch app.

## Installation

### HACS (recommended)

1. In HACS, add this repository as a custom repository (category: Integration).
2. Install "Hatch Sleep".
3. Restart Home Assistant.

### Manual

1. Copy `custom_components/hatch_sleep` into your Home Assistant `config/custom_components`
   directory.
2. Restart Home Assistant.

## Setup

Home Assistant's Bluetooth integration will automatically discover nearby Hatch devices
and offer them under **Settings → Devices & Services**. You can also add one manually via
**Settings → Devices & Services → Add Integration → Hatch Sleep**, which lists any Hatch
devices currently visible to a Bluetooth adapter/proxy.

A Bluetooth adapter (or [Bluetooth proxy](https://www.home-assistant.io/integrations/bluetooth/#remote-adapters-bluetooth-proxies))
in range of the device is required, and only one client can hold an active BLE connection
to the device at a time — close the Hatch mobile app while Home Assistant is connected.

## Protocol credit

The BLE characteristic UUIDs and command format used by this integration were originally
reverse engineered by [kjoconnor](https://github.com/kjoconnor/pyhatchbabyrest). This
integration is an independent implementation built for Home Assistant's local Bluetooth
stack (`bleak` / `bleak-retry-connector`), but the protocol knowledge it relies on
wouldn't exist without that project.

## Limitations

- No battery level, since it isn't reported over this BLE characteristic.
- Only the sounds and colors supported by the original Hatch Rest firmware are exposed.
- This integration actively connects to the device to poll state, which uses more power/
  radio time than a purely passive integration. Polling defaults to once per minute.
