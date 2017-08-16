""" Main script for midi import from notes matrices. """


from midiio.files_io import import_midi_file_from_mat


def main():
    mat_file_path = "data/data_set/Aguado_12valses_Op1_No1.mid_0.npy"
    out_file_path = "data/midi_samples/test.mid"
    import_midi_file_from_mat(mat_file_path, out_file_path, 960, 0)


if __name__ == "__main__":
    main()