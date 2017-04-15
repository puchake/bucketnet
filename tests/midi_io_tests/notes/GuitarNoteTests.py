from src.midi_io.notes.GuitarNote import GuitarNote

import unittest
import numpy as np


class GuitarNoteTestCase(unittest.TestCase):

    def test_convert_to_vector(self):

        # Arrange
        guitar_note = GuitarNote(37, 192, 96)
        pitch_vector = np.zeros([GuitarNote.GUITAR_PITCH_VECTOR_LENGTH, ])
        delta_time_vector = np.zeros([GuitarNote.TIME_VECTOR_LENGTH, ])
        duration_vector = np.zeros([GuitarNote.TIME_VECTOR_LENGTH, ])
        pitch_vector[1] = 1.0
        pitch_vector[GuitarNote.PITCHES_PER_OCTAVE + 1 + 1] = 1.0
        delta_time_vector[7] = 1.0
        delta_time_vector[GuitarNote.TIME_LENGTH_VECTOR_LENGTH] = 1.0
        duration_vector[6] = 1.0
        duration_vector[GuitarNote.TIME_LENGTH_VECTOR_LENGTH] = 1.0

        # Act
        note_vector = guitar_note.convert_to_vector()

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
        pitch_vector = np.zeros([GuitarNote.GUITAR_PITCH_VECTOR_LENGTH, ])
        delta_time_vector = np.zeros([GuitarNote.TIME_VECTOR_LENGTH, ])
        duration_vector = np.zeros([GuitarNote.TIME_VECTOR_LENGTH, ])
        pitch_vector[1] = 1.0
        pitch_vector[GuitarNote.PITCHES_PER_OCTAVE + 1 + 1] = 1.0
        delta_time_vector[7] = 1.0
        delta_time_vector[GuitarNote.TIME_LENGTH_VECTOR_LENGTH + 2] = 1.0
        duration_vector[6] = 1.0
        duration_vector[GuitarNote.TIME_LENGTH_VECTOR_LENGTH] = 1.0
        note_vector = np.concatenate(
            [pitch_vector, delta_time_vector, duration_vector],
            axis=0
        )

        # Act
        guitar_note = GuitarNote.from_vector(note_vector)

        # Assert
        self.assertTrue(
            np.alltrue(guitar_note.convert_to_vector() == note_vector)
        )

    def test_from_values_convert_to_vector(self):

        # Arrange
        pitch_vector = np.zeros([GuitarNote.GUITAR_PITCH_VECTOR_LENGTH, ])
        delta_time_vector = np.zeros([GuitarNote.TIME_VECTOR_LENGTH, ])
        duration_vector = np.zeros([GuitarNote.TIME_VECTOR_LENGTH, ])
        pitch_vector[1] = 1.0
        pitch_vector[GuitarNote.PITCHES_PER_OCTAVE + 1 + 1] = 1.0
        delta_time_vector[7] = 1.0
        delta_time_vector[GuitarNote.TIME_LENGTH_VECTOR_LENGTH + 2] = 1.0
        duration_vector[6] = 1.0
        duration_vector[GuitarNote.TIME_LENGTH_VECTOR_LENGTH] = 1.0
        note_vector = np.concatenate(
            [pitch_vector, delta_time_vector, duration_vector],
            axis=0
        )

        # Act
        guitar_note = GuitarNote.from_values(37, 288, 96)

        # Assert
        self.assertTrue(
            np.alltrue(guitar_note.convert_to_vector() == note_vector)
        )


if __name__ == '__main__':
    unittest.main()
