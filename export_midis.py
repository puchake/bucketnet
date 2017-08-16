""" Main script for midi export to notes matrices. """


from midiio.files_io import export_midi_files_to_mats, export_midi_file_to_mats


def main():
    midi_dir_path = "data/midis"
    transposes = [-2, -1, 1, 2]
    out_dir_path = "data/data_set"
    export_midi_files_to_mats(midi_dir_path, transposes, out_dir_path)


if __name__ == "__main__":
    main()