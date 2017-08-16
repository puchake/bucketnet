"""
This module contains functions used to convert midi tracks/files to notes list
and further to numpy matrices. It also allows conversion from matrix back to the
midi track.
"""


from heapq import heappush, heappop

from mido import MidiFile
import numpy as np

from midiio.note_utils import (note_from_midi, note_from_vec, find_time_unit,
                               transpose_notes, TEMPO_I)
from midiio.midi_utils import create_guitar_track, get_guitar_track_from_file


NUM_OF_PITCHES = 128
DEFAULT_TEMPO = 500000
INVALID_NOTE_I = -1

# Tokens used in notes to track conversion. They are inserted into
# (msg_time, msg) pair, which is pushed on the heap to make sure that the note
# off messages come before note on ones.
ON_MSG_TOKEN = 1
OFF_MSG_TOKEN = 0


def open_note(notes, on_note, current_time, last_on_msg_time, ticks_per_beat,
              current_tempo, open_notes_is, open_notes_times):
    """ Create a new incomplete note and insert it into notes list. """
    notes.append(note_from_midi(on_note, current_time - last_on_msg_time,
                                ticks_per_beat, current_tempo))
    open_notes_is[on_note] = len(notes) - 1
    open_notes_times[on_note] = current_time


def close_note(notes, off_note, current_time, ticks_per_beat, open_notes_is,
               open_notes_times):
    """ Close previously opened incomplete note. """
    notes[open_notes_is[off_note]].duration = find_time_unit(
        current_time - open_notes_times[off_note], ticks_per_beat,
    )
    open_notes_is[off_note] = INVALID_NOTE_I


def close_all_notes(notes, current_time, ticks_per_beat, open_notes_is,
                    open_notes_times):
    """ Close all still not finished notes. """
    for note in range(NUM_OF_PITCHES):
        if open_notes_is[note] != INVALID_NOTE_I:
            close_note(notes, note, current_time, ticks_per_beat, open_notes_is,
                       open_notes_times)


def notes_from_track(track, ticks_per_beat):
    """ Extract notes from track and return list of them. """
    notes = []
    # Arrays used to keep track of where in the notes array the last note with
    # given pitch was placed and at what time it was placed there.
    open_notes_is = [INVALID_NOTE_I] * NUM_OF_PITCHES
    open_notes_times = [INVALID_NOTE_I] * NUM_OF_PITCHES
    current_time = 0
    last_on_msg_time = 0
    current_tempo = DEFAULT_TEMPO
    for msg in track:
        current_time += msg.time
        if msg.type == "note_on" and msg.velocity != 0:
            # If note on this msg's pitch wasn't closed then do it before
            # opening a new note.
            if open_notes_is[msg.note] != INVALID_NOTE_I:
                close_note(notes, msg.note, current_time, ticks_per_beat,
                           open_notes_is, open_notes_times)
            open_note(notes, msg.note, current_time, last_on_msg_time,
                      ticks_per_beat, current_tempo, open_notes_is,
                      open_notes_times)
            last_on_msg_time = current_time
        elif (msg.type == "note_off"
              and open_notes_is[msg.note] != INVALID_NOTE_I
              or msg.type == "note_on" and msg.velocity == 0):
            close_note(notes, msg.note, current_time, ticks_per_beat,
                       open_notes_is, open_notes_times)
        elif msg.type == "set_tempo":
            current_tempo = msg.tempo
    # At the end of conversion close all unfinished notes to ensure not empty
    # note durations.
    close_all_notes(notes, current_time, ticks_per_beat, open_notes_is,
                    open_notes_times)
    return notes


def msgs_heap_from_notes(notes, ticks_per_beat, tempo):
    """
    Transform list of notes into messages and save them on a heap to order them
    by their time.
    """
    heap = []
    last_on_msg_time = 0
    msg_counter = 0
    for note in notes:
        on_msg, off_msg, on_msg_delta_time, off_msg_delta_time = note.to_msgs(
            ticks_per_beat
        )
        # Determine on and off message times.
        on_msg_time = last_on_msg_time + on_msg_delta_time
        off_msg_time = last_on_msg_time + off_msg_delta_time
        last_on_msg_time = on_msg_time
        # Push messages on the heap paired with their type and tokes, so that
        # later, when heappop is used, note off messages will come before note
        # on ones. Include messages counter to break the heappush tie.
        heappush(heap, (on_msg_time, ON_MSG_TOKEN, msg_counter, on_msg))
        heappush(heap, (off_msg_time, OFF_MSG_TOKEN, msg_counter + 1, off_msg))
        msg_counter += 2
    return heap


def track_from_msgs_heap(msgs_heap, tempo, guitar_program_i):
    """ Unroll messages heap to a midi track. """
    track = create_guitar_track(tempo, guitar_program_i)
    prev_msg_time = 0
    while msgs_heap:
        msg_time, _, _, msg = heappop(msgs_heap)
        # Determine this message's delta time from the previous message time.
        msg.time = msg_time - prev_msg_time
        prev_msg_time = msg_time
        track.append(msg)
    return track


def track_from_notes(notes, ticks_per_beat, tempo, guitar_program_i):
    """ Transform list of notes to a midi track. """
    msgs_heap = msgs_heap_from_notes(notes, ticks_per_beat, tempo)
    track = track_from_msgs_heap(msgs_heap, tempo, guitar_program_i)
    return track


def notes_from_mat(mat):
    """ Transform matrix of note vectors to the list of notes. """
    notes = []
    for row in mat:
        notes.append(note_from_vec(row))
    return notes


def mat_from_notes(notes):
    """ Transform list of notes into matrix of note vectors. """
    rows = []
    for note in notes:
        rows.append(note.to_vec())
    mat = np.stack(rows)
    return mat


def track_from_mat(mat, ticks_per_beat, tempo, guitar_program_i):
    """ Transform notes matrix into midi track. """
    notes = notes_from_mat(mat)
    track = track_from_notes(notes, ticks_per_beat, tempo, guitar_program_i)
    return track


def mats_from_midi_file(midi_file, transposes):
    """ Convert midi file directly to list of mats with data augmentation. """
    track = get_guitar_track_from_file(midi_file)
    # If file doesn't contain single guitar track, return empty list.
    if not track:
        return []
    notes = notes_from_track(track, midi_file.ticks_per_beat)
    mats = [mat_from_notes(notes)]
    # Perform data augmentation by transposing notes list.
    for transpose in transposes:
        transposed_notes = transpose_notes(notes, transpose)
        mats.append(mat_from_notes(transposed_notes))
    return mats


def midi_file_from_mat(mat, ticks_per_beat, guitar_program_i):
    """ Convert notes matrix directly to midi file object. """
    # Use single tempo for whole track (maybe temporarily).
    tempo = int(mat[0, TEMPO_I])
    track = track_from_mat(mat, ticks_per_beat, tempo, guitar_program_i)
    midi_file = MidiFile(ticks_per_beat=ticks_per_beat)
    midi_file.tracks.append(track)
    return midi_file
