from .Note import Note
from .NoteTypes import NoteTypes


class DrumsNote (Note):
    """
    Representation of single percussion note.
    """

    # Constant length of 1/0 vector representing drums note pitch.
    #
    # TODO
    DRUMS_PITCH_VECTOR_LENGTH = 0

    def __init__(self, pitch, delta_time, duration):
        super().__init__(NoteTypes.DRUMS_NOTE, pitch, delta_time, duration)

    @classmethod
    def from_values(cls, pitch, delta_time, duration):
        """
        Constructor overload for creating note from values.

        :param pitch: pitch represented as numeric value
        :param delta_time: time from previous note
        :param duration: note's duration
        :return: created note
        """

        drums_note = cls(pitch, delta_time, duration)
        return drums_note

    @classmethod
    def from_vector(cls, vector):
        """
        Constructor overload for creating note from vector.

        :param vector: numpy vector which contains note data
        :return: created note
        """

        # TODO

        pass

    def convert_to_vector(self):
        # TODO

        pass

    def _convert_pitch_to_vector(self):
        # TODO

        pass

    def _convert_vector_to_pitch(self, vector):
        # TODO

        pass