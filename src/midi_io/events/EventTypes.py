from enum import Enum, unique


@unique
class EventTypes (Enum):

    MIDI_EVENT = 0
    META_EVENT = 1
    SYSEX_EVENT = 2
