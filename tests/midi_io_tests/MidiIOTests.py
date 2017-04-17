from src.midi_io.MidiIO import MidiIO

import unittest


class MidiIOTestCase (unittest.TestCase):

    def test_is_midi_file_with_midi_file_1(self):

        # Arrange
        filename = "abc/xyz/name.mid"

        # Act
        result = MidiIO._is_midi_file(filename)

        # Assert
        self.assertEqual(result, True)

    def test_is_midi_file_with_midi_file_2(self):

        # Arrange
        filename = "abc/xyz/ogy/vuw.midi"

        # Act
        result = MidiIO._is_midi_file(filename)

        # Assert
        self.assertEqual(result, True)

    def test_is_midi_file_with_not_midi_file(self):

        # Arrange
        filename = "abc/xyz/ogy/vuw.jpg"

        # Act
        result = MidiIO._is_midi_file(filename)

        # Assert
        self.assertEqual(result, False)

    def test_is_notes_file_with_notes_file(self):

        # Arrange
        filename = "abc/xyz/name.npy"

        # Act
        result = MidiIO._is_notes_file(filename)

        # Assert
        self.assertEqual(result, True)

    def test_is_notes_file_with_not_notes_file(self):

        # Arrange
        filename = "abc/xyz/ogy/vuw.mid"

        # Act
        result = MidiIO._is_notes_file(filename)

        # Assert
        self.assertEqual(result, False)

    def test_get_notes_output_file_paths(self):

        # Arrange
        file_path = "abc/file_1.mid"
        number_of_tracks = 2
        expected_output_paths = [
            "abc/file_1_track_1.npy", "abc/file_1_track_2.npy"
        ]

        # Act
        output_files_paths = MidiIO._get_notes_output_files_paths(
            file_path, number_of_tracks
        )

        # Assert
        self.assertEqual(output_files_paths, expected_output_paths)


if __name__ == '__main__':
    unittest.main()
