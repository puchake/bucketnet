from src.midi_io.notes.DrumsNote import DrumsNote

import unittest
import numpy as np


class DrumsNoteTestCase(unittest.TestCase):

    def test_convert_to_vector(self):

        # Arrange
        drums_note = DrumsNote(37, 72, 72)
        pitch_vector = np.zeros([DrumsNote.DRUMS_PITCH_VECTOR_LENGTH, ])
        delta_time_vector = np.zeros([DrumsNote.TIME_VECTOR_LENGTH, ])
        duration_vector = np.zeros([DrumsNote.TIME_VECTOR_LENGTH, ])
        pitch_vector[2] = 1.0
        delta_time_vector[5] = 1.0
        delta_time_vector[DrumsNote.TIME_LENGTH_VECTOR_LENGTH + 2] = 1.0
        duration_vector[5] = 1.0
        duration_vector[DrumsNote.TIME_LENGTH_VECTOR_LENGTH + 2] = 1.0

        # Act
        note_vector = drums_note.convert_to_vector()

        # Assert
        self.assertTrue(
            np.alltrue(
                np.concatenate(
                    [pitch_vector, delta_time_vector, duration_vector],
                    axis=0
                ) == note_vector
            )
        )

    def test_from_vector_convert_to_vector(self):

        # Arrange
        pitch_vector = np.zeros([DrumsNote.DRUMS_PITCH_VECTOR_LENGTH, ])
        delta_time_vector = np.zeros([DrumsNote.TIME_VECTOR_LENGTH, ])
        duration_vector = np.zeros([DrumsNote.TIME_VECTOR_LENGTH, ])
        pitch_vector[2] = 1.0
        delta_time_vector[5] = 1.0
        delta_time_vector[DrumsNote.TIME_LENGTH_VECTOR_LENGTH + 2] = 1.0
        duration_vector[5] = 1.0
        duration_vector[DrumsNote.TIME_LENGTH_VECTOR_LENGTH + 2] = 1.0
        note_vector = np.concatenate(
            [pitch_vector, delta_time_vector, duration_vector],
            axis=0
        )

        # Act
        drums_note = DrumsNote.from_vector(note_vector)

        # Assert
        self.assertTrue(
            np.alltrue(drums_note.convert_to_vector() == note_vector)
        )

    def test_from_values_convert_to_vector(self):

        # Arrange
        pitch_vector = np.zeros([DrumsNote.DRUMS_PITCH_VECTOR_LENGTH, ])
        delta_time_vector = np.zeros([DrumsNote.TIME_VECTOR_LENGTH, ])
        duration_vector = np.zeros([DrumsNote.TIME_VECTOR_LENGTH, ])
        pitch_vector[2] = 1.0
        delta_time_vector[5] = 1.0
        delta_time_vector[DrumsNote.TIME_LENGTH_VECTOR_LENGTH + 2] = 1.0
        duration_vector[5] = 1.0
        duration_vector[DrumsNote.TIME_LENGTH_VECTOR_LENGTH + 2] = 1.0
        note_vector = np.concatenate(
            [pitch_vector, delta_time_vector, duration_vector],
            axis=0
        )

        # Act
        guitar_note = DrumsNote.from_values(37, 72, 72)

        # Assert
        self.assertTrue(
            np.alltrue(guitar_note.convert_to_vector() == note_vector)
        )


if __name__ == '__main__':
    unittest.main()
