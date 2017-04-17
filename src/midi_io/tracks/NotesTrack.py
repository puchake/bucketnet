from .Track import Track
from .TrackTypes import TrackTypes
from ..notes.GuitarNote import Note
from ..notes.GuitarNote import GuitarNote
from ..notes.DrumsNote import DrumsNote
from ..events.MidiEvent import MidiEvent
from ..events.MidiEventTypes import MidiEventTypes

import numpy as np
import heapq


class NotesTrack (Track):
    """
    Class representing track composed of notes.
    """

    # Constants used to determine event type based on read status code.
    MIN_MIDI_STATUS_CODE = 0x80
    MAX_MIDI_STATUS_CODE = 0xEF
    META_STATUS_CODE = 0xFF

    # Constants used in note start/stop token creation.
    NOTE_START = 1
    NOTE_STOP = 0

    # Default midi channel for guitar track events.
    DEFAULT_CHANNEL = 0

    # Velocity for note ons and offs
    DEFAULT_VELOCITY = 64
    OFF_VELOCITY = 0

    def __init__(self, type, ticks_per_quarter_note):
        super().__init__(type, ticks_per_quarter_note)
        self._notes = []

    @classmethod
    def from_matrix(cls, type, ticks_per_quarter_note, matrix):
        """
        Constructor overload for creating notes track from notes numpy matrix.

        :param ticks_per_quarter_note: midi ticks per quarter note
        :param matrix: numpy matrix which contains notes data
        :return: created notes track
        """

        # Create notes_track object.
        notes_track = cls(type, ticks_per_quarter_note)

        # Get reshaped matrix of notes.
        note_vector_length = Note.TIME_LENGTH_VECTOR_LENGTH * 2
        if type == TrackTypes.GUITAR_TRACK:
            note_vector_length += GuitarNote.GUITAR_PITCH_VECTOR_LENGTH
            reshaped_matrix = np.reshape(matrix, [-1, note_vector_length])
        else:
            note_vector_length += DrumsNote.DRUMS_PITCH_VECTOR_LENGTH
            reshaped_matrix = np.reshape(matrix, [-1, note_vector_length])

        # For every note stored in matrix:
        for i in range(reshaped_matrix.shape[0]):

            # Read note from current unwrapped_matrix row and append it
            # to track notes.
            notes_track._read_note(reshaped_matrix[i])

        return notes_track

    @classmethod
    def from_notes(cls, type, ticks_per_quarter_note, notes):
        """
        Constructor overload for creating notes track from array of notes.

        :param type: previously determined track type
        :param ticks_per_quarter_note: midi ticks per quarter note
        :param notes: array of input notes
        :return: created notes track
        """

        # Create notes_track object and set its notes list
        # to list provided as function argument.
        notes_track = cls(type, ticks_per_quarter_note)
        notes_track._notes = notes

        return notes_track

    def convert_to_events(self):
        """
        Convert track's notes to events.

        :return: array of events
        """

        # Initialize empty events and note tokens lists.
        events = []
        note_tokens = []
        time = 0

        # Push start and stop tokens of every note on heap.
        for note in self._notes:
            time += note.get_delta_time()
            start, stop = self._get_note_start_stop(time, note)
            heapq.heappush(note_tokens, start)
            heapq.heappush(note_tokens, stop)

        # Determine midi output channel.
        if self._type == TrackTypes.GUITAR_TRACK:
            channel = NotesTrack.DEFAULT_CHANNEL
        else:
            channel = MidiEvent.DRUMS_CHANNEL

        # Get tokens in order from the earliest to the latest and
        # append events created from them to events list.
        time = 0
        while note_tokens:
            token = heapq.heappop(note_tokens)
            midi_event = NotesTrack._convert_token_to_event(
                time, token, channel
            )
            events.append(midi_event)
            time = token[0]

        return events

    def get_wrapped_notes_matrix(self, matrix_wrap, notes_frame_width):
        """
        Convert notes from this track to matrix of notes frames in which
        every frame overlaps with the next and previous one and contains
        matrix_wrap unique notes not present in the next frame.

        :param matrix_wrap: number of unique notes per frame
        :param notes_frame_width:
        :return: wrapped notes matrix
        """

        # Create empty notes vectors list.
        notes_vectors_list = []

        # For every note currently present in track:
        for note in self._notes:

            # Append its vector representation to list.
            notes_vectors_list.append(note.convert_to_vector())

        # Create matrix from vectors list.
        notes_matrix = np.array(notes_vectors_list)

        # Return its wrapped form.
        return NotesTrack._wrap_notes_matrix(notes_matrix, matrix_wrap, notes_frame_width)

    def _read_note(self, vector):
        """
        Read and append note from provided vector to instance array.

        :param vector: numpy vector containing note data
        :return: -
        """

        # If it is guitar track create new guitar note. Else create drum note.
        if self._type == TrackTypes.GUITAR_TRACK:
            note = GuitarNote.from_vector(vector)
        else:
            note = DrumsNote.from_vector(vector)

        self._notes.append(note)

    def _get_note_start_stop(self, time, note):
        """
        Converts note to pair of start/stop tokens.

        :param time: note start time in note time units
        :param note: note to convert
        :return: pair of tokens, points in time indicating note's start and
                 stop.
        """

        # Gather note's data.
        pitch = note.get_pitch()
        duration = note.get_duration()

        # Create start and stop tokens.
        start = [time * self._min_ticks_per_note, pitch, NotesTrack.NOTE_START]
        stop = [
            (time + duration) * self._min_ticks_per_note,
            pitch,
            NotesTrack.NOTE_STOP
        ]

        return start, stop

    @staticmethod
    def _convert_token_to_event(time, token, channel):
        """
        Get event representing given token.

        :param time: time of previous token conversion
        :param token: token to convert
        :param channel: channel to which event should belong
        :return: created event
        """

        #Unpack token
        token_time, pitch, token_type = token

        # Based on token_type return note on or note off event.
        if token_type == NotesTrack.NOTE_START:
            return MidiEvent.from_values(
                token_time - time,
                MidiEventTypes.NOTE_ON,
                [pitch, NotesTrack.DEFAULT_VELOCITY]
            )
        else:
            return MidiEvent.from_values(
                token_time - time,
                MidiEventTypes.NOTE_OFF,
                [pitch, NotesTrack.OFF_VELOCITY]
            )

    @staticmethod
    def _wrap_notes_matrix(matrix, matrix_wrap, notes_frame_width):
        """
        Convert continuous notes matrix to its wrapped form with notes frames.

        :param matrix: numpy matrix of notes
        :param matrix_wrap: value telling us how many notes from one notes
                            frame are unique and not present in the next one
        :param notes_frame_width: length of notes vector representing
                                  one note frame
        :return: wrapped matrix
        """

        # Get parameters necessary to wrap a notes matrix.
        number_of_notes = matrix.shape[0]
        note_vector_size = matrix.shape[1]
        repeated_notes_per_frame = notes_frame_width - matrix_wrap

        # Calculate number of available notes frames.
        number_of_frames = (number_of_notes - repeated_notes_per_frame) // \
                           matrix_wrap

        # Create wrapped matrix.
        wrapped_matrix = np.empty(
            [notes_frame_width, number_of_frames, note_vector_size]
        )

        for i in range(number_of_frames):

            # Extract correct matrix fragment and store it as notes frame in
            # wrapped matrix.
            wrapped_matrix[i] = matrix[
                i * matrix_wrap:
                i * matrix_wrap + notes_frame_width
            ]

        return wrapped_matrix

    @staticmethod
    def _unwrap_notes_matrix(matrix, matrix_wrap):
        """
        Convert wrapped matrix to its continuous form.

        :param matrix: numpy matrix of notes frames
        :param matrix_wrap: value telling us how many notes from one notes
                            frame are unique and not present in the next one
        :return: unwrapped matrix
        """

        # Initialize empty list to store all extracted note fragments.
        notes_fragments_list = []

        # For every notes frame in matrix:
        for i in range(matrix.shape[0]):

            # Append its unique fragment to list.
            notes_fragments_list.append(matrix[i, :matrix_wrap])

        # Return all unique notes fragments concatenated together.
        return np.concatenate(notes_fragments_list)