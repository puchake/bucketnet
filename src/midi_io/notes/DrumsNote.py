from .Note import Note
from .NoteTypes import NoteTypes

import numpy as np


class DrumsNote (Note):
    """
    Representation of single percussion note.
    """

    # Constant length of 1/0 vector representing drums note pitch.
    # 22 for used percussion notes which belong to midi percussion notes set
    # 1 for pause
    DRUMS_PITCH_VECTOR_LENGTH = 22 + 1

    # List of recognised drums pitches + pause pitch.
    DRUMS_PITCH_LIST = list(range(35, 54)) + [55, 57, 59, -1]

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

        # Initialize "empty" note.
        drums_note = cls(0, 0, 0)

        # Fill it by calling instance convert methods with
        # appropriate input vector parts.
        drums_note._convert_vector_to_pitch(
            vector[:DrumsNote.DRUMS_PITCH_VECTOR_LENGTH]
        )
        drums_note._convert_vector_to_delta_time(
            vector[
                DrumsNote.DRUMS_PITCH_VECTOR_LENGTH:
                DrumsNote.DRUMS_PITCH_VECTOR_LENGTH + Note.TIME_VECTOR_LENGTH
            ]
        )
        drums_note._convert_vector_to_duration(
            vector[
                DrumsNote.DRUMS_PITCH_VECTOR_LENGTH +
                Note.TIME_VECTOR_LENGTH:
            ]
        )

        return drums_note

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

        # Create zeros vector of required length and set it to 1
        # at right position.
        pitch_vector = np.zeros([DrumsNote.DRUMS_PITCH_VECTOR_LENGTH, ])
        pitch_index = DrumsNote.DRUMS_PITCH_LIST.index(self._pitch)
        pitch_vector[pitch_index] = 1.0

        return pitch_vector

    def _convert_vector_to_pitch(self, vector):
        """
        Fill note's pitch field with data from vector.

        :param vector: pitch saved as vector
        :return: -
        """

        # Find pitch index and set this note's pitch to
        # value from DRUMS_PITCH_LIST chosen by index.
        pitch_index = np.argmax(vector)
        self._pitch = DrumsNote.DRUMS_PITCH_LIST[pitch_index]