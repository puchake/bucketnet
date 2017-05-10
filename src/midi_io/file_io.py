import midi_io.events_handling as events_handling
import midi_io.notes_handling as notes_handling
import midi_io.track_conversion as track_conversion

import struct
from io import BytesIO
import numpy as np
from os import path


# Constants for reading values from midi file.
CHUNK_HEADER_SIZE = 4
INT_SIZE = 4
SHORT_SIZE = 2

# Recognizable chunk headers.
HEADER_HEADER = b'MThd'
TRACK_HEADER = b'MTrk'

# Constant default header length for midi file.
DEFAULT_HEADER_LENGTH = 6

# Default values for midi header parameters.
DEFAULT_MIDI_TYPE = 1
DEFAULT_NUMBER_OF_TRACKS = 1

# Timing related constants.
NOTES_TIME_UNITS_PER_QUARTER_NOTE = 48
DEFAULT_TICKS_PER_QUARTER_NOTE = 960

# Constant string for files extensions.
NOTES_FILE_EXTENSION = ".notes"
DEFAULT_MIDI_FILE_EXTENSION = ".midi"


def read_midi_file(source):
    """
    Parse midi file into events list with midi file parameters.
    Only first not empty track is parsed ! ! ! ! ! ! !
    :param source: object which contains midi file bytes
    :return: ticks per quarter note and list of events
    """

    number_of_tracks, ticks_per_quarter_note = read_midi_header(source)
    events = []

    # Keep reading tracks until non empty track is read or until all tracks
    # are read.
    for i in range(number_of_tracks):
        events = read_midi_track(source)
        if not events_handling.is_events_list_empty(events):
            break
        else:
            events = []

    return ticks_per_quarter_note, events


def read_midi_header(source):
    """
    Extract number of tracks and ticks per quarter note from midi header.
    :param source: source for reading
    :return: number of tracks and ticks per quarter note
    """

    header_header = source.read(CHUNK_HEADER_SIZE)
    header_length = struct.unpack(">I", source.read(INT_SIZE))[0]

    # Read midi file parameters.
    midi_type = struct.unpack(">H", source.read(SHORT_SIZE))[0]
    number_of_tracks = struct.unpack(">H", source.read(SHORT_SIZE))[0]
    ticks_per_quarter_note = struct.unpack(">H", source.read(SHORT_SIZE))[0]

    # Read remaining header bytes if necessary.
    source.read(header_length - DEFAULT_HEADER_LENGTH)

    return number_of_tracks, ticks_per_quarter_note


def read_midi_track(source):
    """
    Parse midi track intro list of events or simply read whole midi chunk if it
    is not recognized.
    :param source: source for reading
    :return: list of read events
    """

    track_header = source.read(CHUNK_HEADER_SIZE)
    track_length = struct.unpack(">I", source.read(INT_SIZE))[0]

    # If read chunk is not recognized read its content and return empty list.
    if track_header != TRACK_HEADER or track_length == 0:
        source.read(track_length)
        return []

    # Read all track events.
    events = []
    while True:
        events.append(events_handling.read_event(source))
        if events_handling.is_end_of_track(events[-1]):
            break

    return events


def write_midi_file(destination, ticks_per_quarter_note, events):
    """
    Output list of events and ticks per quarter note to new midi file. One
    list of events is single track.
    :param destination: destination for writing
    :param ticks_per_quarter_note: track parameter, ticks per quarter note
    :param events: list of track events
    :return: -
    """

    write_midi_header(destination, ticks_per_quarter_note)
    write_midi_track(destination, events)


def write_midi_header(destination, ticks_per_quarter_note):
    """
    Output midi header bytes to destination.
    :param destination: destination for writing
    :param ticks_per_quarter_note: midi ticks per quarter note
    :return: -
    """

    destination.write(HEADER_HEADER)
    destination.write(struct.pack(">I", DEFAULT_HEADER_LENGTH))
    destination.write(struct.pack(">H", DEFAULT_MIDI_TYPE))
    destination.write(struct.pack(">H", DEFAULT_NUMBER_OF_TRACKS))
    destination.write(struct.pack(">H", ticks_per_quarter_note))


def write_midi_track(destination, events):
    """
    Output events list to midi file as track.
    :param destination: destination for writing
    :param events: list of events which are going to be written to file
    :return: -
    """

    destination.write(TRACK_HEADER)

    # Output all events to temporary buffer, because length of track in bytes
    # must be known to output it as chunk length beforehand.
    track_events_destination = BytesIO(b'')
    for event in events:
        events_handling.write_event(track_events_destination, event)

    track_events_bytes = track_events_destination.getbuffer()
    destination.write(struct.pack(">I", len(track_events_bytes)))
    destination.write(track_events_bytes)


def read_notes_file(source):
    """
    Parse numpy notes file into list of notes.
    :param source: bytes of notes file
    :return: notes_type and list of notes
    """

    notes_type, matrix_wrap, notes_frame_width = read_notes_header(source)

    # Determine note vector length.
    if notes_type == notes_handling.GUITAR_NOTE:
        note_vector_length = notes_handling.GUITAR_PITCH_VECTOR_LENGTH + \
                             2 * notes_handling.TIME_VECTOR_LENGTH
    else:
        note_vector_length = notes_handling.DRUMS_PITCH_VECTOR_LENGTH + \
                             2 * notes_handling.TIME_VECTOR_LENGTH

    # Read notes matrix and reshape it to wrapped notes matrix.
    #wrapped_notes_matrix = np.fromfile(source).reshape(
    #    [-1, notes_frame_width, note_vector_length]
    #)
    #
    #notes_matrix = notes_handling.unwrap_notes_matrix(
    #    wrapped_notes_matrix, matrix_wrap, notes_frame_width
    #)
    notes_matrix = np.fromfile(source).reshape([-1, note_vector_length])
    notes = []

    # Convert all note vectors to their note representations.
    for i in range(notes_matrix.shape[0]):
        notes.append(
            notes_handling.create_note_from_vector(notes_type, notes_matrix[i])
        )

    return notes_type, notes


def read_notes_header(source):
    """
    Read notes file parameters from start of file.
    :param source: bytes of notes file
    :return: notes type, notes matrix wrap and its note frame width
    """

    notes_type = np.fromfile(source, dtype=np.int32, count=1)[0]
    matrix_wrap = np.fromfile(source, dtype=np.int32, count=1)[0]
    notes_frame_width = np.fromfile(source, dtype=np.int32, count=1)[0]

    return notes_type, matrix_wrap, notes_frame_width


def write_notes_file(
    destination, notes_type, matrix_wrap, notes_frame_width, notes
):
    """
    Output list of notes to binary file.
    :param destination: destination for writing
    :param notes_type: type of outputted notes
    :param matrix_wrap: value telling us how many notes from one notes
                        frame are unique and not present in the next one
    :param notes_frame_width: number of notes per frame
    :param notes: list of outputted notes
    :return: -
    """

    write_notes_header(destination, notes_type, matrix_wrap, notes_frame_width)

    # Determine note vector length.
    if notes_type == notes_handling.GUITAR_NOTE:
        note_vector_length = notes_handling.GUITAR_PITCH_VECTOR_LENGTH + \
                             2 * notes_handling.TIME_VECTOR_LENGTH
    else:
        note_vector_length = notes_handling.DRUMS_PITCH_VECTOR_LENGTH + \
                             2 * notes_handling.TIME_VECTOR_LENGTH

    # Create and fill notes matrix.
    notes_matrix = np.empty([len(notes), note_vector_length])
    for i in range(notes_matrix.shape[0]):
        notes_matrix[i] = notes_handling.convert_note_to_vector(notes[i])

    notes_matrix.tofile(destination)
    # Create and output to file wrapped notes matrix.
    #wrapped_notes_matrix = notes_handling.wrap_notes_matrix(
    #    notes_matrix, matrix_wrap, notes_frame_width
    #)
    #wrapped_notes_matrix.tofile(destination)


def write_notes_header(
    destination, notes_type, matrix_wrap, notes_frame_width
):
    """
    Output notes file header.
    :param destination: destination for writing
    :param notes_type: type of outputted notes
    :param matrix_wrap: value telling us how many notes from one notes
                        frame are unique and not present in the next one
    :param notes_frame_width: number of notes per frame
    :return: -
    """

    parameters = np.array([notes_type, matrix_wrap, notes_frame_width])
    parameters.tofile(destination)


def export_midi_to_notes(
        midi_file_path, output_path, matrix_wrap, notes_frame_width
):
    """
    Export midi file to notes file.
    :param midi_file_path: path to the midi file
    :param output_path: path to output directory
    :return: -
    """

    # Open and read midi file.
    midi_file = open(midi_file_path, "rb")
    ticks_per_quarter_note, events = read_midi_file(midi_file)
    midi_file.close()

    ticks_per_note_time_unit = ticks_per_quarter_note // \
                               NOTES_TIME_UNITS_PER_QUARTER_NOTE
    notes_type, notes = track_conversion.convert_events_to_notes(
        events, ticks_per_quarter_note, ticks_per_note_time_unit
    )

    # Create and fill notes file.
    notes_base_filename, _ = path.splitext(path.basename(midi_file_path))
    notes_base_filename += NOTES_FILE_EXTENSION
    notes_file_path = path.join(output_path, notes_base_filename)
    notes_file = open(notes_file_path, "wb")
    write_notes_file(
        notes_file, notes_type, matrix_wrap, notes_frame_width, notes
    )
    notes_file.close()


def export_notes_to_midi(notes_file_path, output_path):
    """
    Export notes file to midi file.
    :param notes_file_path: path to the notes file
    :param output_path: path to output directory
    :return: -
    """

    # Open and read notes file.
    notes_file = open(notes_file_path, "rb")
    notes_type, notes = read_notes_file(notes_file)
    notes_file.close()

    ticks_per_note_time_unit = DEFAULT_TICKS_PER_QUARTER_NOTE // \
                               NOTES_TIME_UNITS_PER_QUARTER_NOTE
    events = track_conversion.convert_notes_to_events(
        notes_type, notes, ticks_per_note_time_unit
    )

    # Create and fill midi file.
    midi_base_filename, _ = path.splitext(path.basename(notes_file_path))
    midi_base_filename += DEFAULT_MIDI_FILE_EXTENSION
    midi_file_path = path.join(output_path, midi_base_filename)
    midi_file = open(midi_file_path, "wb")
    write_midi_file(midi_file, DEFAULT_TICKS_PER_QUARTER_NOTE, events)
    midi_file.close()
