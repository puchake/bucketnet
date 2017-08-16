"""
This module contains functions, which allow conversion from both raw midi events
and RNN numpy input to the intermediate Note object format. It also provides
Note class definition and handles further conversion from Note to numpy vectors.
"""

from copy import copy

from mido import Message
import numpy as np


# Boundaries for accepted pitches.
LOWEST_PITCH = 30
HIGHEST_PITCH = 101
NUM_OF_PITCHES = HIGHEST_PITCH - LOWEST_PITCH + 1

# Array of recognized time units. Each midi time interval is brought to the
# closest matching value from this matrix and saved as pair of indices.
RECOGNIZED_TIME_UNITS = np.append([0], np.power(2.0, range(-7, 2, 1)))
NUM_OF_TIME_UNITS = 10

# Note's pitch, offset and duration will be all encoded in one-hot format, so
# guitar note vector representation should have enough elements to encode every
# accepted pitch as well as two times the every recognized time unit and one
# float value for tempo.
NOTE_VEC_LEN = NUM_OF_PITCHES + 2 * NUM_OF_TIME_UNITS + 1

PITCH_FIRST_I = 0
OFFSET_FIRST_I = NUM_OF_PITCHES
DURATION_FIRST_I = OFFSET_FIRST_I + NUM_OF_TIME_UNITS
TEMPO_I = DURATION_FIRST_I + NUM_OF_TIME_UNITS
BEATS_IN_FULL_NOTE = 4
DEFAULT_VELOCITY = 64


class Note:
    """
    Class with represents object which is intermediate between midi event and
    RNN input vector.
    """

    def __init__(self, pitch, offset, duration, tempo):
        self.pitch = pitch
        self.offset = offset
        self.duration = duration
        self.tempo = tempo

    def to_vec(self):
        """ Convert note to its vector representation. """
        vec = np.zeros([NOTE_VEC_LEN])
        # Save pitch, offset and duration in one-hot format.
        vec[PITCH_FIRST_I + self.pitch - LOWEST_PITCH] = 1.0
        vec[OFFSET_FIRST_I + self.offset] = 1.0
        vec[DURATION_FIRST_I + self.duration] = 1.0
        vec[TEMPO_I] = self.tempo
        return vec

    def to_msgs(self, ticks_per_beat):
        """ Convert note to a pair of on and off note midi messages """
        on_msg = Message(type="note_on")
        off_msg = Message(type="note_off")
        on_msg.note = self.pitch
        off_msg.note = self.pitch
        on_msg.velocity = DEFAULT_VELOCITY
        on_msg_delta_time = int(RECOGNIZED_TIME_UNITS[self.offset]
                                * ticks_per_beat
                                * BEATS_IN_FULL_NOTE)
        off_msg_delta_time = (on_msg_delta_time
                              + int(RECOGNIZED_TIME_UNITS[self.duration]
                                    * ticks_per_beat
                                    * BEATS_IN_FULL_NOTE))
        return on_msg, off_msg, on_msg_delta_time, off_msg_delta_time

    def transpose(self, half_steps):
        """ Transpose the note by given amount of half steps. """
        self.pitch += half_steps


def find_time_unit(ticks, ticks_per_beat):
    """ Match input time in midi ticks to the closest recognized time unit. """
    time = ticks / ticks_per_beat / BEATS_IN_FULL_NOTE
    return np.argmin(np.abs(RECOGNIZED_TIME_UNITS - time))


def note_from_vec(vec):
    """ Create new note object from vector data. """
    # Retrieve pitch, offset and duration kept in one-hot format.
    pitch = (np.argmax(vec[PITCH_FIRST_I:PITCH_FIRST_I + NUM_OF_PITCHES])
             + LOWEST_PITCH)
    offset = np.argmax(vec[OFFSET_FIRST_I:OFFSET_FIRST_I + NUM_OF_TIME_UNITS])
    duration = np.argmax(
        vec[DURATION_FIRST_I:DURATION_FIRST_I + NUM_OF_TIME_UNITS]
    )
    tempo = vec[TEMPO_I]
    return Note(pitch, offset, duration, tempo)


def note_from_midi(pitch, offset_ticks, ticks_per_beat, tempo):
    """ Create new incomplete note object from midi variables. """
    offset = find_time_unit(offset_ticks, ticks_per_beat)
    return Note(pitch, offset, None, tempo)


def transpose_notes(notes, half_steps):
    """ Transpose whole list of notes and copy it. """
    transposed_notes = [copy(note) for note in notes]
    for note in transposed_notes:
        note.transpose(half_steps)
    return transposed_notes
