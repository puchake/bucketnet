from enum import Enum, unique


@unique
class NoteTypes (Enum):
    """
    Enumeration for used note types.
    """

    GUITAR_NOTE = 0
    DRUMS_NOTE = 1