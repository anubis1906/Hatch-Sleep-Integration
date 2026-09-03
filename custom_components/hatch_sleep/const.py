"""Constants for the Hatch Sleep integration."""
from __future__ import annotations

import logging

DOMAIN = "hatch_sleep"
LOGGER = logging.getLogger(__package__)

DEFAULT_NAME = "Hatch Sleep"
MANUFACTURER = "Hatch"

# BLE manufacturer ID broadcast by Hatch Rest / Rest Mini / Rest+ (1st-gen) devices,
# used for both passive bluetooth discovery and active scanning.
BT_MANUFACTURER_ID = 1076

# GATT characteristics exposed by the device's custom service. These were
# reverse engineered by the community (see README for credit) and are shared
# across Hatch Rest, Rest Mini and Rest+ (1st-gen) hardware.
CHAR_TX = "02240002-5efd-47eb-9c1a-de53f7a2b232"
CHAR_FEEDBACK = "02260002-5efd-47eb-9c1a-de53f7a2b232"

# Byte offsets in the CHAR_FEEDBACK notification/read payload.
FEEDBACK_COLOR_MARKER_INDEX = 5
FEEDBACK_COLOR_MARKER = 0x43
FEEDBACK_RED_INDEX = 6
FEEDBACK_GREEN_INDEX = 7
FEEDBACK_BLUE_INDEX = 8
FEEDBACK_BRIGHTNESS_INDEX = 9
FEEDBACK_AUDIO_MARKER_INDEX = 10
FEEDBACK_AUDIO_MARKER = 0x53
FEEDBACK_SOUND_INDEX = 11
FEEDBACK_VOLUME_INDEX = 12
FEEDBACK_POWER_MARKER_INDEX = 13
FEEDBACK_POWER_MARKER = 0x50
FEEDBACK_POWER_STATE_INDEX = 14
FEEDBACK_POWER_STATE_MASK = 0b11000000
FEEDBACK_MIN_LENGTH = 15

UPDATE_SECONDS = 60
COMMAND_SETTLE_SECONDS = 0.25

MIN_VOLUME = 0
MAX_VOLUME = 100
DEFAULT_ON_BRIGHTNESS = 255

# Sound name -> value understood by the "SN" command, as reverse engineered
# from the official Hatch app/firmware. Gaps in the numbering are sounds that
# only exist on other Hatch hardware revisions.
SOUND_NAME_TO_VALUE: dict[str, int] = {
    "none": 0,
    "stream": 2,
    "white_noise": 3,
    "dryer": 4,
    "ocean": 5,
    "wind": 6,
    "rain": 7,
    "bird": 9,
    "crickets": 10,
    "brahms_lullaby": 11,
    "twinkle_twinkle": 13,
    "rock_a_bye": 14,
}
SOUND_VALUE_TO_NAME: dict[int, str] = {v: k for k, v in SOUND_NAME_TO_VALUE.items()}
