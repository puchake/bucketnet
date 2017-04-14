from .Track import Track
from .TrackTypes import TrackTypes
from ..notes.GuitarNote import GuitarNote
from ..notes.DrumsNote import DrumsNote


class NotesTrack (Track):
    """
    Class representing track composed of notes.
    """

    # Constants used to determine event type based on read status code.
    MIN_MIDI_STATUS_CODE = 0x80
    MAX_MIDI_STATUS_CODE = 0xEF
    META_STATUS_CODE = 0xFF

    def __init__(self, type, ticks_per_quarter_note):
        super().__init__(type, ticks_per_quarter_note)
        self._notes = []

    @classmethod
    def from_matrix(cls, type, ticks_per_quarter_note, matrix):
        """
        Constructor overload for creating notes track from notes numpy matrix.

        :param ticks_per_quarter_note: midi ticks per quarter note
        :param matrix: numpy matrix which contains notes data
        :return: created notes track
        """

        notes_track = cls(type, ticks_per_quarter_note)

        # TODO

        return notes_track

    @classmethod
    def from_notes(cls, type, ticks_per_quarter_note, notes):
        """
        Constructor overload for creating notes track from array of notes.

        :param type: previously determined track type
        :param ticks_per_quarter_note: midi ticks per quarter note
        :param notes: array of input notes
        :return: created notes track
        """

        notes_track = cls(type, ticks_per_quarter_note)

        # TODO

        return notes_track

    def convert_to_events(self):
        """
        Convert track's notes to events.

        :return: array of events
        """

        # TODO

        pass

    def _read_note(self, vector):
        """
        Read and append note from provided vector to instance array.

        :param vector: numpy vector containing note data
        :return: -
        """

        # If it is guitar track create new guitar note. Else create drum note.
        if self._type == TrackTypes.GUITAR_TRACK:
            note = GuitarNote.from_vector(vector)
        else:
            note = DrumsNote.from_vector(vector)

        self._notes.append(note)