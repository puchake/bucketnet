from enum import Enum, unique


@unique
class MidiEventTypes (Enum):
    """
    Enum for available midi event types.
    """

    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    POLYPHONIC_PRESSURE = 0xA0
    CONTROLLER = 0xB0
    PROGRAM_CHANGE = 0xC0
    CHANNEL_PRESSURE = 0xD0
    PITCH_BEND = 0xE0