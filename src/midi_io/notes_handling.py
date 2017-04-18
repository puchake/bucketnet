from collections import namedtuple
import numpy as np


# Create Note named tuple.
Note = namedtuple("Note", ["type", "pitch", "delta_time", "duration"])

# Available notes types.
GUITAR_NOTE = 0
DRUMS_NOTE = 1

# Constant value representing pitch of a pause.
PAUSE_PITCH = -1

# Constants defining available guitar's pitch range.
MIN_GUITAR_PITCH = 24
MAX_GUITAR_PITCH = 95

# List of recognised drums pitches + pause pitch.
DRUMS_PITCH_LIST = list(range(35, 54)) + [55, 57, 59, -1]

# Constant pitches per octave and number of octaves for guitar's pitch.
PITCHES_PER_OCTAVE = 12
NUMBER_OF_OCTAVES = 6

# Constant length of 1/0 vector representing guitar note pitch. +1 for pause.
GUITAR_PITCH_VECTOR_LENGTH = PITCHES_PER_OCTAVE + 1 + NUMBER_OF_OCTAVES

# Constant guitar's pitch vector index for pause.
GUITAR_PITCH_VECTOR_PAUSE_INDEX = PITCHES_PER_OCTAVE

# Length of 1/0 drums pitch vector.
DRUMS_PITCH_VECTOR_LENGTH = len(DRUMS_PITCH_LIST)

# Constants describing length of time interval vector representation.
TIME_LENGTH_VECTOR_LENGTH = 8
TIME_TYPE_VECTOR_LENGTH = 3
TIME_VECTOR_LENGTH = TIME_LENGTH_VECTOR_LENGTH + TIME_TYPE_VECTOR_LENGTH

# Array of allowed time interval values (delta times and durations). First row
# is intervals of normal notes, second is for triplets and last is for dotted
# notes.
POSSIBLE_TIMINGS = np.tile(np.append([0], [2.0] ** np.arange(7)), (3, 1)) * \
                   [[3.0], [2.0], [4.5]]

# Indices used in accessing POSSIBLE_TIMINGS search results.
TIME_INDEX_TYPE_PART = 0
TIME_INDEX_LENGTH_PART = 1


def create_note_from_vector(type, note_vector):
    """
    Create note from data vector, basing on provided note's type.
    :param type: type of the note contained in vector
    :param note_vector: vector containing note's data
    :return: created note
    """

    # Determine pitch part length, basing on type.
    if type == GUITAR_NOTE:
        pitch_part_length = GUITAR_PITCH_VECTOR_LENGTH
    else:
        pitch_part_length = DRUMS_PITCH_VECTOR_LENGTH

    # Split note vector for pitch, delta time and duration parts.
    pitch_part, delta_time_part, duration_part = np.split(
        note_vector,
        [pitch_part_length, pitch_part_length + TIME_VECTOR_LENGTH]
    )

    pitch = convert_vector_to_pitch(type, pitch_part)
    delta_time = convert_vector_to_time(delta_time_part)
    duration = convert_vector_to_time(duration_part)

    return Note(type, pitch, delta_time, duration)


def convert_note_to_vector(note):
    """
    Convert note to its vector representation.
    :param note: converted note
    :return: vector which is result of the conversion
    """

    # Convert note's pitch, delta time and duration to vectors.
    pitch_vector = convert_pitch_to_vector(note.type, note.pitch)
    delta_time_vector = convert_time_to_vector(note.delta_time)
    duration_vector = convert_time_to_vector(note.duration)

    return np.concatenate([pitch_vector, delta_time_vector, duration_vector])

def convert_pitch_to_vector(type, pitch):
    """
    Convert given pitch to its 1/0 vector representation.
    :param type: type of converted pitch
    :param pitch: converted pitch
    :return: result vector
    """

    if type == GUITAR_NOTE:
        pitch_vector = np.zeros([GUITAR_PITCH_VECTOR_LENGTH, ])

        # Find pitch and octave indices for input pitch and set them to 1.0
        # in pitch vector.
        if pitch == PAUSE_PITCH:
            pitch_index = GUITAR_PITCH_VECTOR_PAUSE_INDEX
        else:
            pitch_index = (pitch - MIN_GUITAR_PITCH) % PITCHES_PER_OCTAVE

        # Calculate octave index and clip it to 0 - NUMBER_OF_OCTAVES - 1
        # bounds.
        octave_index = max((pitch - MIN_GUITAR_PITCH) // PITCHES_PER_OCTAVE, 0)
        octave_index = min(octave_index, NUMBER_OF_OCTAVES - 1)

        pitch_vector[pitch_index] = 1.0
        pitch_vector[PITCHES_PER_OCTAVE + 1 + octave_index] = 1.0

    else:
        pitch_vector = np.zeros([DRUMS_PITCH_VECTOR_LENGTH, ])

        # Find index for input pitch from available drums pitches and set
        # correct element in pitch vector to 1.0.
        pitch_index = DRUMS_PITCH_LIST.index(pitch)
        pitch_vector[pitch_index] = 1.0

    return pitch_vector


def convert_vector_to_pitch(type, vector):
    """
    Convert vector with pitch data inside it to pitch value.
    :param type: type of pitch represented by vector
    :param vector: pitch saved as vector
    :return: pitch which is result of the conversion
    """

    if type == GUITAR_NOTE:

        # Find pitch and octave indices.
        pitch_index = np.argmax(vector[:PITCHES_PER_OCTAVE + 1])
        octave_index = np.argmax(vector[PITCHES_PER_OCTAVE + 1:])

        if pitch_index == GUITAR_PITCH_VECTOR_PAUSE_INDEX:
            return PAUSE_PITCH
        else:
            return MIN_GUITAR_PITCH + pitch_index + \
                   octave_index * PITCHES_PER_OCTAVE

    else:

        # Find out which pitch is saved in vector and return it.
        pitch_index = np.argmax(vector)
        return DRUMS_PITCH_LIST[pitch_index]


def convert_time_to_vector(time):
    """
    Convert time value to 1/0 vector.
    :param time: converted time value
    :return: vector which is conversion result
    """

    # Get closest available time value index by searching through
    # POSSIBLE_TIMINGS.
    time_index = np.unravel_index(
        np.argmin(np.absolute(POSSIBLE_TIMINGS - time)), POSSIBLE_TIMINGS.shape
    )

    time_type = np.zeros([TIME_TYPE_VECTOR_LENGTH, ])
    time_length = np.zeros([TIME_LENGTH_VECTOR_LENGTH, ])

    # Save 1.0 on positions found in searching of closest matching time value.
    time_type[time_index[TIME_INDEX_TYPE_PART]] = 1.0
    time_length[time_index[TIME_INDEX_LENGTH_PART]] = 1.0

    return np.concatenate([time_length, time_type])


def convert_vector_to_time(vector):
    """
    Convert 1/0 vector to time value.
    :param vector: vector with time data inside it
    :return: converted time value
    """

    # Determine POSSIBLE_TIMINGS indices for time value saved in vector.
    time_type_index = np.argmax(vector[TIME_LENGTH_VECTOR_LENGTH:])
    time_length_index = np.argmax(vector[:TIME_LENGTH_VECTOR_LENGTH])

    return POSSIBLE_TIMINGS[time_type_index, time_length_index]


def wrap_notes_matrix(matrix, matrix_wrap, notes_frame_width):
    """
    Convert continuous notes matrix to its wrapped form.
    :param matrix: numpy matrix of notes in vectors form
    :param matrix_wrap: value telling us how many notes from one notes
                        frame are unique and not present in the next one
    :param notes_frame_width: number of notes per frame
    :return: wrapped notes matrix
    """

    number_of_notes = matrix.shape[0]
    note_vector_size = matrix.shape[1]
    repeated_notes_per_frame = notes_frame_width - matrix_wrap

    # Calculate number of available notes frames.
    number_of_frames = (number_of_notes - repeated_notes_per_frame) // \
                       matrix_wrap

    wrapped_matrix = np.empty(
        [number_of_frames, notes_frame_width, note_vector_size]
    )
    for i in range(number_of_frames):

        # Extract correct matrix fragment and store it as notes frame in
        # wrapped matrix.
        wrapped_matrix[i] = matrix[
            i * matrix_wrap:
            i * matrix_wrap + notes_frame_width
        ]

    return wrapped_matrix


def unwrap_notes_matrix(wrapped_matrix, matrix_wrap, notes_frame_width):
    """
    Convert wrapped notes matrix to its continuous form.
    :param wrapped_matrix: numpy matrix of notes frames
    :param matrix_wrap: value telling us how many notes from one notes
                        frame are unique and not present in the next one
    :param notes_frame_width: number of notes per frame
    :return: unwrapped notes matrix
    """

    number_of_frames = wrapped_matrix.shape[0]
    note_vector_size = wrapped_matrix.shape[2]

    unwrapped_matrix = np.empty(
        [number_of_frames * matrix_wrap, note_vector_size]
    )
    for i in range(number_of_frames):

        # From each notes frame extract unique notes and store them in
        # unwrapped notes matrix.
        unwrapped_matrix[i * matrix_wrap:(i + 1) * matrix_wrap] = \
            wrapped_matrix[i, :matrix_wrap]

    return unwrapped_matrix
