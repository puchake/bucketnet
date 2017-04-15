from .Note import Note
from .NoteTypes import NoteTypes

import numpy as np


class GuitarNote (Note):
    """
    Representation of single guitar note.
    """

    # Constant pitches per octave and number of octaves.
    PITCHES_PER_OCTAVE = 12
    NUMBER_OF_OCTAVES = 6

    # Constant length of 1/0 vector representing guitar note pitch.
    # 12 for one out of A, A#, B, C, ...
    # 1 for pause (no sound)
    # 6 for octave
    GUITAR_PITCH_VECTOR_LENGTH = PITCHES_PER_OCTAVE + 1 + NUMBER_OF_OCTAVES

    # Constants defining available pitch range.
    MIN_PITCH = 24
    MAX_PITCH = 95

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

        # Initialize "empty" note.
        guitar_note = cls(0, 0, 0)

        # Fill it by calling instance convert methods with
        # appropriate input vector parts.
        guitar_note._convert_vector_to_pitch(
            vector[:GuitarNote.GUITAR_PITCH_VECTOR_LENGTH]
        )
        guitar_note._convert_vector_to_delta_time(
            vector[
                GuitarNote.GUITAR_PITCH_VECTOR_LENGTH:
                GuitarNote.GUITAR_PITCH_VECTOR_LENGTH + Note.TIME_VECTOR_LENGTH
            ]
        )
        guitar_note._convert_vector_to_duration(
            vector[
                GuitarNote.GUITAR_PITCH_VECTOR_LENGTH +
                Note.TIME_VECTOR_LENGTH:
            ]
        )

        return guitar_note

    def convert_to_vector(self):
        """
        Obtain vector representation of this note.

        :return: constructed vector representing this note
        """

        # Return concatenated results of note fields conversions.
        return np.concatenate(
            [
                self._convert_pitch_to_vector(),
                self._convert_delta_time_to_vector(),
                self._convert_duration_to_vector()
            ],
            axis=0
        )

    def _convert_pitch_to_vector(self):
        """
        Convert this note's pitch field to its vector representation.

        :return: result vector
        """

        # Create zeros vector of required length.
        pitch_vector = np.zeros([GuitarNote.GUITAR_PITCH_VECTOR_LENGTH, ])

        # If converted note is not a pause then calculate its vector index.
        # Else set the index for last element of vector's pitch part.
        if self._pitch != Note.PAUSE_PITCH:
            pitch_index = (self._pitch - GuitarNote.MIN_PITCH) % \
                          GuitarNote.PITCHES_PER_OCTAVE
        else:
            pitch_index = GuitarNote.PITCHES_PER_OCTAVE

        # Calculate octave index and transform it if it exceeds 0 - 5 bounds
        # (for example when converted note is pause).
        octave_index = (self._pitch - GuitarNote.MIN_PITCH) // \
                       GuitarNote.PITCHES_PER_OCTAVE
        octave_index = min(octave_index, GuitarNote.NUMBER_OF_OCTAVES - 1)
        octave_index = max(octave_index, 0)

        # Set proper parts of pitch_vector to 1.
        pitch_vector[pitch_index] = 1.0
        pitch_vector[GuitarNote.PITCHES_PER_OCTAVE + 1 + octave_index] = 1.0

        return pitch_vector

    def _convert_vector_to_pitch(self, vector):
        """
        Fill note's pitch field with data from vector.

        :param vector: pitch saved as vector
        :return: -
        """

        # Find pitch and octave indices.
        pitch_index = np.argmax(vector[:GuitarNote.PITCHES_PER_OCTAVE + 1])
        octave_index = np.argmax(vector[GuitarNote.PITCHES_PER_OCTAVE + 1:])

        # If found pitch_index is pause index set pitch to PAUSE_PITCH.
        # Else calculate pitch using found indices.
        if pitch_index == GuitarNote.PITCHES_PER_OCTAVE:
            self._pitch = Note.PAUSE_PITCH
        else:
            self._pitch = GuitarNote.MIN_PITCH + pitch_index + \
                          octave_index * GuitarNote.PITCHES_PER_OCTAVE