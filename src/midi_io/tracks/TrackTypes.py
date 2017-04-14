from enum import Enum, unique


@unique
class TrackTypes (Enum):
    """
    Track types enumeration.
    """

    NOT_DETERMINED = 0
    GUITAR_TRACK = 1
    DRUMS_TRACK = 2