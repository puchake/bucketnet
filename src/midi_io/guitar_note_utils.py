"""
This module contains functions, which allow conversion from both raw midi events
and NN numpy input to the intermediate GuitarNote format. It also provides
GuitarNote class definition.
"""


from mido import second2tick, tick2second
import numpy as np


# Boundaries for accepted pitches.
LOWEST_PITCH = 30
HIGHEST_PITCH = 101

NUM_OF_PITCHES = HIGHEST_PITCH - LOWEST_PITCH + 1

MAX_VELOCITY = 127

# Note's pitch will be encoded in one-hot format, so guitar note vector
# representation should have enough elements to encode every accepted pitch
# as well as single float values for velocity, delta_time and duration.
NOTE_VEC_LEN = NUM_OF_PITCHES + 3

# Indices of
VELOCITY_I = -3
DELTA_TIME_I = -2
DURATION_I = -1
PITCH_FIRST_I = 0


class GuitarNote:
    """
    Container for guitar midi note.
    """

    def __init__(self, pitch, velocity, delta_time, duration):
        """
        :param pitch: pitch of the sound
        :type pitch: integer in range 0 ... 127
        :param velocity: volume of the sound
        :type velocity: integer in range 0 ... 127
        :param delta_time: offset of midi ticks from the previous note's start
        :type delta_time: positive integer
        :param duration: duration of the sound in midi ticks
        :type duration: positive integer
        """
        self.pitch = pitch
        self.velocity = velocity
        self.delta_time = delta_time
        self.duration = duration

    def to_vec(self, ticks_per_beat, tempo):
        """
        Transform the note to vector and return it.

        :param ticks_per_beat: number of midi ticks per midi beat
        :type ticks_per_beat: float or int
        :param tempo: microseconds per midi beat
        :type tempo: float or int
        :return: vector, which contains note data
        """
        vec = np.zeros([NOTE_VEC_LEN])
        vec[PITCH_FIRST_I + self.pitch - LOWEST_PITCH] = 1.0
        vec[VELOCITY_I] = self.velocity / MAX_VELOCITY
        vec[DELTA_TIME_I] = tick2second(self.delta_time, ticks_per_beat, tempo)
        vec[DURATION_I] = tick2second(self.duration, ticks_per_beat, tempo)

    def transpose(self, half_steps):
        """
        Transpose the note by given amount of half steps.

        :param half_steps: number of half steps to transpose the note by. Can be
                           negative
        :type half_steps: integer
        :return: -
        """
        self.pitch += half_steps


def from_vec(vec, ticks_per_beat, tempo):
    """
    Create guitar note from note data kept in vector.

    :param vec: vector, which contains note's data
    :type vec: numpy vector of floats with NOTE_VEC_LEN elements
    :param ticks_per_beat: number of midi ticks per midi beat
    :type ticks_per_beat: float or int
    :param tempo: microseconds per midi beat
    :type tempo: float or int
    :return: created GuitarNode object
    """
    pitch = (
        np.argmax(vec[PITCH_FIRST_I:PITCH_FIRST_I + NUM_OF_PITCHES])
        + LOWEST_PITCH
    )
    velocity = int(vec[VELOCITY_I] * MAX_VELOCITY)
    delta_time = int(second2tick(vec[DELTA_TIME_I], ticks_per_beat, tempo))
    duration = int(second2tick(vec[DURATION_I], ticks_per_beat, tempo))
    return GuitarNote(pitch, velocity, delta_time, duration, tempo)


def from_on_msg(on_msg, delta_time, tempo):
    """
    Create guitar note object from the note on midi message.

    :param on_msg: midi message of the start of note playback
    :type on_msg: mido Message object with "note_on" type
    :param delta_time: time in midi ticks from the last "note_on" event
    :type delta_time: integer not less than 0
    :param tempo: microseconds per midi beat
    :type tempo: float or int
    :return: created GuitarNote object
    """
    return GuitarNote(on_msg.note, on_msg.velocity, delta_time, None, tempo)
