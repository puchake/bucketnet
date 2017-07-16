"""
This module contains functions, which allow conversion from both raw midi events
and NN numpy input to the intermediate Note object format. It also provides
Note class definition and handles further conversion from Note to numpy vectors.
"""


from mido import Message
import numpy as np


# Boundaries for accepted pitches.
LOWEST_PITCH = 30
HIGHEST_PITCH = 101
NUM_OF_PITCHES = HIGHEST_PITCH - LOWEST_PITCH + 1

# Length modifiers for each of the recognized time interval types.
DOTTED_TIME_MOD = 1.5
NORMAL_TIME_MOD = 1.0
TRIPLET_TIME_MOD = 2.0 / 3.0
NUM_OF_TIME_TYPES = 3

# All recognized base note lengths - 0, 1/128th, ..., quarter, halt, full and
# two times the duration of a full note. This vector along with time modifiers
# is used to construct matrix of recognized time units.
NORMAL_NOTE_LENGTHS = np.append([0], np.power(2.0, range(-7, 2, 1)))
NUM_OF_NOTE_LENGTHS = 10

# Array of recognized time units. Each midi time interval is brought to the
# closest matching value from this matrix and saved as pair of indices.
RECOGNIZED_TIME_UNITS = np.dot(
    [[DOTTED_TIME_MOD], [NORMAL_TIME_MOD], [TRIPLET_TIME_MOD]],
    [NORMAL_NOTE_LENGTHS]
)
NUM_OF_TIME_UNITS = NUM_OF_TIME_TYPES * NUM_OF_NOTE_LENGTHS

# Note's pitch, offset and duration will be all encoded in one-hot format, so
# guitar note vector representation should have enough elements to encode every
# accepted pitch as well as two times the every recognized time unit and two
# single float values - one for note's tempo and other for its velocity.
NOTE_VEC_LEN = NUM_OF_PITCHES + 2 * NUM_OF_TIME_UNITS + 2

# Indices of pitch, offset, duration, tempo and velocity parts in note's vector
# representation.
PITCH_FIRST_I = 0
OFFSET_FIRST_I = NUM_OF_PITCHES
DURATION_FIRST_I = OFFSET_FIRST_I + NUM_OF_TIME_UNITS
TEMPO_I = DURATION_FIRST_I + NUM_OF_TIME_UNITS
VELOCITY_I = TEMPO_I + 1

# Number of the beats, which correspond to one full note. It is used in time
# conversion.
BEATS_IN_FULL_NOTE = 4


class Note:
    """
    Container for midi notes.
    """

    def __init__(self, pitch, offset, duration, velocity, tempo):
        """
        :param pitch: pitch of the sound
        :type pitch: integer in range 0 ... 127
        :param offset: offset from the previous note's start saved as indices to
                       the correct element in RECOGNIZED_TIME_UNITS matrix
        :type offset: tuple of 2 positive integers
        :param duration: duration of the note saved also as indices to the
                         correct element in RECOGNIZED_TIME_UNITS matrix
        :type duration: tuple of 2 positive integers
        :param velocity: volume of the sound
        :type velocity: numeric value in range 0 ... 127
        :param tempo: tempo at which the sound was played
        :type tempo: positive numeric value
        """
        self.pitch = pitch
        self.offset = offset
        self.duration = duration
        self.velocity = velocity
        self.tempo = tempo

    def to_vec(self):
        """
        Transform the note to vector and return it.

        :return: vector, which contains note data
        """
        vec = np.zeros([NOTE_VEC_LEN])
        # Save pitch, offset and duration in one-hot format.
        vec[PITCH_FIRST_I + self.pitch - LOWEST_PITCH] = 1.0
        vec[
            OFFSET_FIRST_I
            + np.ravel_multi_index(self.offset, RECOGNIZED_TIME_UNITS.shape)
        ] = 1.0
        vec[
            DURATION_FIRST_I
            + np.ravel_multi_index(self.duration, RECOGNIZED_TIME_UNITS.shape)
        ] = 1.0
        vec[VELOCITY_I] = self.velocity
        vec[TEMPO_I] = self.tempo
        return vec

    def to_msgs(self, ticks_per_beat, tempo):
        """
        Convert note to a pair of on and off note midi messages and their
        timings relative to the previous note's start time.

        :param ticks_per_beat: number of midi ticks per midi beat
        :type ticks_per_beat: float or int
        :return: created pair of mido midi messages
        """
        on_msg = Message(type="note_on")
        off_msg = Message(type="note_off")
        on_msg.note = self.pitch
        off_msg.note = self.pitch
        on_msg.velocity = self.velocity
        on_msg_delta_time = int(
            self.offset * ticks_per_beat * BEATS_IN_FULL_NOTE
        )
        off_msg_delta_time = (
            on_msg_delta_time
            + int(self.duration * ticks_per_beat * BEATS_IN_FULL_NOTE)
        )
        return on_msg, off_msg, on_msg_delta_time, off_msg_delta_time

    def transpose(self, half_steps):
        """
        Transpose the note by given amount of half steps.

        :param half_steps: number of half steps to transpose the note by. Can be
                           negative
        :type half_steps: integer
        :return: -
        """
        self.pitch += half_steps


def find_time_unit(ticks, ticks_per_beat):
    """
    Match input time in midi ticks to the closest recognized time unit.

    :param ticks: midi time in ticks
    :type ticks: positive integer
    :param ticks_per_beat: number of ticks per quarter note
    :param ticks_per_beat: positive integer
    :return: pair of indices to the matched time unit from the
             RECOGNIZED_TIME_UNITS matrix
    """
    time = ticks / ticks_per_beat / BEATS_IN_FULL_NOTE
    return np.unravel_index(
        np.argmin(np.abs(RECOGNIZED_TIME_UNITS - time)),
        RECOGNIZED_TIME_UNITS.shape
    )


def from_vec(vec):
    """
    Create guitar note from note data kept in vector.

    :param vec: vector, which contains note's data
    :type vec: numpy vector of floats with NOTE_VEC_LEN elements
    :return: created Note object
    """
    # Retrieve pitch, offset and duration kept in one-hot format.
    pitch = (
        np.argmax(vec[PITCH_FIRST_I:PITCH_FIRST_I + NUM_OF_PITCHES])
        + LOWEST_PITCH
    )
    offset = np.unravel_index(
        np.argmax(vec[OFFSET_FIRST_I:OFFSET_FIRST_I + NUM_OF_TIME_UNITS]),
        RECOGNIZED_TIME_UNITS.shape
    )
    duration = np.unravel_index(
        np.argmax(vec[DURATION_FIRST_I:DURATION_FIRST_I + NUM_OF_TIME_UNITS]),
        RECOGNIZED_TIME_UNITS.shape
    )
    velocity = vec[VELOCITY_I]
    tempo = vec[TEMPO_I]
    return Note(pitch, offset, duration, velocity, tempo)


def from_on_msg(on_msg, offset_ticks, ticks_per_beat, tempo):
    """
    Create guitar note object from the note on midi message.

    :param on_msg: midi message of the start of note playback
    :type on_msg: mido Message object with "note_on" type
    :param offset_ticks: time in midi ticks from the last "note_on" event
    :type offset_ticks: integer not less than 0
    :param ticks_per_beat: number of midi ticks per midi beat
    :type ticks_per_beat: float or int
    :param tempo: microseconds per midi beat
    :type tempo: float or int
    :return: created Note object
    """
    pitch = on_msg.note
    velocity = on_msg.velocity
    offset = find_time_unit(offset_ticks, ticks_per_beat)
    duration = None
    return Note(pitch, offset, duration, velocity, tempo)
