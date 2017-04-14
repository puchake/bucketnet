from .Note import Note
from .NoteTypes import NoteTypes


class GuitarNote (Note):
    """
    Representation of single guitar note.
    """

    # Constant length of 1/0 vector representing guitar note pitch.
    # 12 for one out of A, A#, B, C, ...
    # 5 for octave
    GUITAR_PITCH_VECTOR_LENGTH = 12 + 5

    def __init__(self, pitch, delta_time, duration):
        super().__init__(NoteTypes.GUITAR_NOTE, pitch, delta_time, duration)

    @classmethod
    def from_values(cls, pitch, delta_time, duration):
        """
        Constructor overload for creating note from values.

        :param pitch: pitch represented as numeric value
        :param delta_time: time from previous note
        :param duration: note's duration
        :return: created note
        """

        guitar_note = cls(pitch, delta_time, duration)
        return guitar_note

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