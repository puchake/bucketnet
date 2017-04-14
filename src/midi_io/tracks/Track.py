from .TrackTypes import TrackTypes

from abc import ABC, abstractmethod


class Track (ABC):
    """
    Abstract base class for other track classes.
    """

    # Constant multiplier which applied to ticks_per_quarter_note read
    # from midi file gives track time unit in which note durations will be
    # represented.
    #
    # 1/16 - 1/64 note, 1/3 - half of a duration of note in triplet
    #
    # So 1/64 note is 3 units long, 1/32 is 6 units long and so on.
    MIN_NOTE_DURATION_MULTIPLIER = 1 / 16 * 1 / 3

    def __init__(self, type, ticks_per_quarter_note):
        """
        Initialize track with its type and ticks_per_quarter_note.

        :param type: TrackTypes value describing track instrument
        :param ticks_per_quarter_note: number of delta-time ticks per
                                       quarter note
        """

        self._type = type
        self._min_ticks_per_note = Track.MIN_NOTE_DURATION_MULTIPLIER * \
                                   ticks_per_quarter_note

    def get_type(self):
        """
        Get track type.

        :return: track type
        """

        return self._type

    def _convert_to_track_time_unit(self, ticks):
        """
        Converts time in midi ticks to track time units.

        :param ticks: time in midi ticks
        :return: ticks converted to track time unit
        """

        return ticks / self._min_ticks_per_note

    def _convert_to_midi_ticks(self, time):
        """
        Converts time tracks units to midi ticks.

        :param time: time represented in track time units
        :return: time converted to midi ticks
        """

        return time * self._min_ticks_per_note