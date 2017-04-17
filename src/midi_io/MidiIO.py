from .files.MidiFile import MidiFile
from .files.NotesFile import NotesFile

from os import path, listdir
import numpy as np


class MidiIO:
    """
    Entry point for midi export and import.
    """

    # Recognized midi file and notes file extensions.
    MIDI_EXTENSIONS = [".mid", ".midi"]
    NOTES_EXTENSIONS = [".npy"]

    @classmethod
    def export_midi_to_notes(
        cls, input_dir=".", output_dir=".", files_list=None
    ):
        """
        Transform data from midi files to notes.
        :param input_dir: input directory path
        :param output_dir: output directory path
        :param files_list: list of exported files
        :return: -
        """

        if not files_list:
            files_list = listdir(input_dir)

        for filename in files_list:
            if cls._is_midi_file(filename):

                # Open midi file extract its tracks as notes and save them
                # in separate files.
                file_path = path.join(input_dir, filename)
                midi_file = MidiFile(file_path)
                notes_matrices = midi_file.get_notes_matrices()
                number_of_tracks = len(notes_matrices)
                output_files_paths = cls._get_notes_output_files_paths(
                    file_path, number_of_tracks
                )
                for i in range(number_of_tracks):
                    np.save(output_files_paths[i], notes_matrices[i])

    @classmethod
    def import_notes_to_midi(
        cls, input_dir=".", output_dir=".", files_list=None
    ):
        """
        Transform data from notes files to midi.
        :return: -
        """

        if not files_list:
            files_list = listdir(input_dir)

        for filename in files_list:
            if cls._is_notes_file(filename):

                # Open notes file, transform it into midi file bytes
                # and save it.
                file_path = path.join(input_dir, filename)
                notes_file = NotesFile(file_path)
                midi_bytes = notes_file.get_bytes()
                base_file_path, _ = path.splitext(
                    path.join(output_dir, filename)
                )
                output_file_path = path.join(
                    base_file_path, cls.MIDI_EXTENSIONS[0]
                )
                midi_file = open(output_file_path, "wb")
                midi_file.write(midi_bytes)
                midi_file.close()

    @classmethod
    def _is_midi_file(cls, filename):
        """
        Check if file extension matches recognized midi files extensions.
        :return: check result
        """

        _, extension = path.splitext(filename)
        return extension in cls.MIDI_EXTENSIONS

    @classmethod
    def _is_notes_file(cls, filename):
        """
        Check if file extension matches recognized notes files extensions.
        :return: check result
        """

        _, extension = path.splitext(filename)
        return extension in cls.NOTES_EXTENSIONS

    @classmethod
    def _get_notes_output_files_paths(cls, file_path, number_of_tracks):
        """
        Get list of files paths for notes files to export.
        :param file_path: file path for export
        :param number_of_tracks: number of exported tracks
        :return: list of files paths
        """

        base_file_path, _ = path.splitext(file_path)
        output_files_paths = []

        # Construct output paths.
        for i in range(1, number_of_tracks + 1):
            output_files_paths.append(
                base_file_path +
                "_track_{}".format(i) +
                cls.NOTES_EXTENSIONS[0]
            )

        return output_files_paths