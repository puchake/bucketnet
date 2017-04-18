import src.midi_io.notes_handling as notes_handling

import unittest
import numpy as np


class NotesHandlingTestCase (unittest.TestCase):

    def test_convert_time_to_vector_normal(self):

        # Arrange
        time = 96
        expected_vector = np.array(
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0]
        )

        # Act
        vector = notes_handling.convert_time_to_vector(time)

        # Assert
        self.assertTrue(np.alltrue(vector == expected_vector))

    def test_convert_time_to_vector_triplet(self):

        # Arrange
        time = 32
        expected_vector = np.array(
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        )

        # Act
        vector = notes_handling.convert_time_to_vector(time)

        # Assert
        self.assertTrue(np.alltrue(vector == expected_vector))

    def test_convert_time_to_vector_dotted(self):

        # Arrange
        time = 36
        expected_vector = np.array(
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        )

        # Act
        vector = notes_handling.convert_time_to_vector(time)

        # Assert
        self.assertTrue(np.alltrue(vector == expected_vector))

    def test_convert_vector_to_time_normal(self):

        # Arrange
        vector = np.array(
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0]
        )
        expected_time = 192

        # Act
        time = notes_handling.convert_vector_to_time(vector)

        # Assert
        self.assertEqual(time, expected_time)

    def test_convert_vector_to_time_triplet(self):

        # Arrange
        vector = np.array(
            [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        )
        expected_time = 2

        # Act
        time = notes_handling.convert_vector_to_time(vector)

        # Assert
        self.assertEqual(time, expected_time)

    def test_convert_vector_to_time_dotted(self):

        # Arrange
        vector = np.array(
            [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        )
        expected_time = 9

        # Act
        time = notes_handling.convert_vector_to_time(vector)

        # Assert
        self.assertEqual(time, expected_time)

    def test_convert_pitch_to_vector_guitar_pitch(self):

        # Arrange
        pitch = 32
        expected_vector = np.zeros(notes_handling.GUITAR_PITCH_VECTOR_LENGTH)
        expected_vector[8] = 1.0
        expected_vector[13] = 1.0

        # Act
        vector = notes_handling.convert_pitch_to_vector(
            notes_handling.GUITAR_NOTE, pitch
        )

        # Assert
        self.assertTrue(np.alltrue(vector == expected_vector))

    def test_convert_pitch_to_vector_drums_pitch(self):

        # Arrange
        pitch = 53
        expected_vector = np.zeros(notes_handling.DRUMS_PITCH_VECTOR_LENGTH)
        expected_vector[18] = 1.0

        # Act
        vector = notes_handling.convert_pitch_to_vector(
            notes_handling.DRUMS_NOTE, pitch
        )

        # Assert
        self.assertTrue(np.alltrue(vector == expected_vector))

    def test_convert_vector_to_pitch_guitar_pitch(self):

        # Arrange
        vector = np.zeros([notes_handling.GUITAR_PITCH_VECTOR_LENGTH, ])
        vector[12] = 1.0
        vector[14] = 1.0
        expected_pitch = -1

        # Act
        pitch = notes_handling.convert_vector_to_pitch(
            notes_handling.GUITAR_NOTE, vector
        )

        # Assert
        self.assertEqual(pitch, expected_pitch)

    def test_convert_vector_to_pitch_drums_pitch(self):

        # Arrange
        vector = np.zeros([notes_handling.DRUMS_PITCH_VECTOR_LENGTH, ])
        vector[12] = 1.0
        expected_pitch = 47

        # Act
        pitch = notes_handling.convert_vector_to_pitch(
            notes_handling.DRUMS_NOTE, vector
        )

        # Assert
        self.assertEqual(pitch, expected_pitch)

    def test_create_note_from_vector_guitar_note(self):

        # Arrange
        pitch_vector = notes_handling.convert_pitch_to_vector(
            notes_handling.GUITAR_NOTE, 30
        )
        delta_time_vector = notes_handling.convert_time_to_vector(72)
        duration_vector = notes_handling.convert_time_to_vector(96)
        vector = np.concatenate(
            [pitch_vector, delta_time_vector, duration_vector]
        )
        expected_note = notes_handling.Note(
            notes_handling.GUITAR_NOTE, 30, 72, 96
        )

        # Act
        note = notes_handling.create_note_from_vector(
            notes_handling.GUITAR_NOTE, vector
        )

        # Assert
        self.assertEqual(expected_note, note)

    def test_create_note_from_vector_drums_note(self):

        # Arrange
        pitch_vector = notes_handling.convert_pitch_to_vector(
            notes_handling.DRUMS_NOTE, 37
        )
        delta_time_vector = notes_handling.convert_time_to_vector(36)
        duration_vector = notes_handling.convert_time_to_vector(192)
        vector = np.concatenate(
            [pitch_vector, delta_time_vector, duration_vector]
        )
        expected_note = notes_handling.Note(
            notes_handling.DRUMS_NOTE, 37, 36, 192
        )

        # Act
        note = notes_handling.create_note_from_vector(
            notes_handling.DRUMS_NOTE, vector
        )

        # Assert
        self.assertEqual(expected_note, note)

    def test_convert_note_to_vector_guitar_note(self):

        # Arrange
        note = notes_handling.Note(
            notes_handling.GUITAR_NOTE, 36, 18, 48
        )
        pitch_vector = notes_handling.convert_pitch_to_vector(
            notes_handling.GUITAR_NOTE, 36
        )
        delta_time_vector = notes_handling.convert_time_to_vector(18)
        duration_vector = notes_handling.convert_time_to_vector(48)
        expected_vector = np.concatenate(
            [pitch_vector, delta_time_vector, duration_vector]
        )

        # Act
        vector = notes_handling.convert_note_to_vector(note)

        # Assert
        self.assertTrue(np.alltrue(vector == expected_vector))

    def test_convert_note_to_vector_drums_note(self):

        # Arrange
        note = notes_handling.Note(
            notes_handling.DRUMS_NOTE, -1, 288, 3
        )
        pitch_vector = notes_handling.convert_pitch_to_vector(
            notes_handling.DRUMS_NOTE, -1
        )
        delta_time_vector = notes_handling.convert_time_to_vector(288)
        duration_vector = notes_handling.convert_time_to_vector(3)
        expected_vector = np.concatenate(
            [pitch_vector, delta_time_vector, duration_vector]
        )

        # Act
        vector = notes_handling.convert_note_to_vector(note)

        # Assert
        self.assertTrue(np.alltrue(vector == expected_vector))

    def test_wrap_notes_matrix_guitar_notes(self):

        # Arrange
        note_vector_length = notes_handling.GUITAR_PITCH_VECTOR_LENGTH + \
                             2 * notes_handling.TIME_VECTOR_LENGTH
        notes_matrix = np.empty([20, note_vector_length])
        for i in range(20):
            notes_matrix[i] = notes_handling.convert_note_to_vector(
                notes_handling.Note(
                    notes_handling.GUITAR_NOTE, 30 + i, 96, 96
                )
            )
        expected_matrix = np.empty([9, 4, note_vector_length])
        for i in range(9):
            expected_matrix[i] = notes_matrix[2 * i:2 * i + 4]

        # Act
        wrapped_matrix = notes_handling.wrap_notes_matrix(notes_matrix, 2, 4)

        # Assert
        self.assertTrue(np.alltrue(wrapped_matrix == expected_matrix))

    def test_wrap_notes_matrix_drum_notes(self):

        # Arrange
        note_vector_length = notes_handling.DRUMS_PITCH_VECTOR_LENGTH + \
                             2 * notes_handling.TIME_VECTOR_LENGTH
        notes_matrix = np.empty([15, note_vector_length])
        for i in range(15):
            notes_matrix[i] = notes_handling.convert_note_to_vector(
                notes_handling.Note(
                    notes_handling.DRUMS_NOTE, 35 + i, 72, 192
                )
            )
        expected_matrix = np.empty([6, 4, note_vector_length])
        for i in range(6):
            expected_matrix[i] = notes_matrix[2 * i:2 * i + 4]

        # Act
        wrapped_matrix = notes_handling.wrap_notes_matrix(notes_matrix, 2, 4)

        # Assert
        self.assertTrue(np.alltrue(wrapped_matrix == expected_matrix))


    def test_unwrap_notes_matrix_with_wrap(self):

        # Arrange
        note_vector_length = notes_handling.DRUMS_PITCH_VECTOR_LENGTH + \
                             2 * notes_handling.TIME_VECTOR_LENGTH
        notes_matrix = np.empty([15, note_vector_length])
        for i in range(15):
            notes_matrix[i] = notes_handling.convert_note_to_vector(
                notes_handling.Note(
                    notes_handling.DRUMS_NOTE, 35 + i, 72, 192
                )
            )
        expected_matrix = np.empty([6, 4, note_vector_length])
        for i in range(6):
            expected_matrix[i] = notes_matrix[2 * i:2 * i + 4]
        wrapped_matrix = notes_handling.wrap_notes_matrix(notes_matrix, 2, 4)

        # Act
        unwrapped_matrix = notes_handling.unwrap_notes_matrix(
            wrapped_matrix, 2, 4
        )

        # Assert
        self.assertTrue(np.alltrue(unwrapped_matrix == notes_matrix[:12]))

    def test_unwrap_notes_matrix_with_no_wrap(self):

        # Arrange
        note_vector_length = notes_handling.DRUMS_PITCH_VECTOR_LENGTH + \
                             2 * notes_handling.TIME_VECTOR_LENGTH
        notes_matrix = np.empty([15, note_vector_length])
        for i in range(15):
            notes_matrix[i] = notes_handling.convert_note_to_vector(
                notes_handling.Note(
                    notes_handling.DRUMS_NOTE, 35 + i, 72, 192
                )
            )
        expected_matrix = np.empty([15, 1, note_vector_length])
        for i in range(15):
            expected_matrix[i] = notes_matrix[1 * i:1 * i + 1]
        wrapped_matrix = notes_handling.wrap_notes_matrix(notes_matrix, 1, 1)

        # Act
        unwrapped_matrix = notes_handling.unwrap_notes_matrix(
            wrapped_matrix, 1, 1
        )

        # Assert
        self.assertTrue(np.alltrue(unwrapped_matrix == notes_matrix))


if __name__ == '__main__':
    unittest.main()
