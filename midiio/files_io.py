"""
This module contains midi export and import functions which allow
conversions on the file/directory path level.
"""


from os import path, listdir

from mido import MidiFile
import numpy as np

from midiio.conversions import mats_from_midi_file, midi_file_from_mat


def export_midi_file_to_mats(midi_file_path, transposes, out_dir_path):
    """ Export single midi file to notes matrices and save them as files. """
    midi_file = MidiFile(midi_file_path)
    mats = mats_from_midi_file(midi_file, transposes)
    file_basename = path.basename(midi_file_path)
    for i, mat in enumerate(mats):
        np.save(path.join(out_dir_path, file_basename + "_" + str(i)), mat)


def import_midi_file_from_mat(mat_file_path, out_file_path, ticks_per_beat,
                              guitar_program_i):
    """ Import midi file from notes matrix file. """
    mat = np.load(mat_file_path)
    midi_file = midi_file_from_mat(mat, ticks_per_beat, guitar_program_i)
    midi_file.save(out_file_path)


def export_midi_files_to_mats(midi_dir_path, transposes, out_dir_path):
    """
    Export all midi files found under given directory path to notes matrices and
    save them.
    """
    for filename in listdir(midi_dir_path):
        try:
            print("{} - {}".format(filename, "Processing file."))
            export_midi_file_to_mats(path.join(midi_dir_path, filename),
                                     transposes, out_dir_path)
            print("{} - {}".format(filename, "Processing done."))
        except (IOError, ValueError):
            print("{} - {}".format(filename, "Corrupted file."))
