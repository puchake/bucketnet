from .Track import Track
from .TrackTypes import TrackTypes
from ..events.MidiEvent import MidiEvent
from ..events.MetaEvent import MetaEvent
from ..events.SysexEvent import SysexEvent
from ..notes.Note import Note
from ..notes.GuitarNote import GuitarNote
from ..notes.DrumsNote import DrumsNote


class EventsTrack (Track):
    """
    Class representing track composed of events.
    """

    # Max interval length in quarter notes.
    MAX_INTERVAL = 4

    # Indices of timings and events in note on/off events pairs.
    START_TIME_INDEX = 0
    START_EVENT_INDEX = 1
    END_TIME_INDEX = 2
    END_EVENT_INDEX = 3

    # Indices of notes values.
    DELTA_TIME_INDEX = 1
    DURATION_INDEX = 2

    # Sizes of events history vectors for guitar and drums tracks.
    GUITAR_HISTORY_SIZE = GuitarNote.PITCHES_PER_OCTAVE * \
                          GuitarNote.NUMBER_OF_OCTAVES
    DRUMS_HISTORY_SIZE = DrumsNote.DRUMS_PITCH_VECTOR_LENGTH - 1

    # Constants used to determine event type based on read status code.
    MIN_MIDI_STATUS_CODE = 0x80
    MAX_MIDI_STATUS_CODE = 0xEF
    META_STATUS_CODE = 0xFF

    def __init__(self, type, ticks_per_quarter_note):
        super().__init__(type, ticks_per_quarter_note)
        self._events = []
        self._max_time_interval = EventsTrack.MAX_INTERVAL * \
                                  ticks_per_quarter_note

    @classmethod
    def from_bytes(cls, ticks_per_quarter_note, source):
        """
        Constructor overload for creating events track from raw midi bytes.

        :param ticks_per_quarter_note: midi ticks per quarter note
        :param source: MidiBytesIO object, source for reading
        :return: created events track
        """

        # Create track object.
        events_track = cls(TrackTypes.NOT_DETERMINED, ticks_per_quarter_note)

        # Interpret bytes from source as events and save them to events track
        # until end of track event is read and saved.
        while True:
            event = events_track._read_event(source)
            if event.is_end_of_track():
                break

        # Determine whether it is guitar or drums track.
        events_track._determine_type()

        return events_track

    @classmethod
    def from_events(cls, type, ticks_per_quarter_note, events):
        """
        Constructor overload for creating events track from array of events.

        :param type: already determined track type
        :param ticks_per_quarter_note: midi ticks per quarter note
        :param events: array of events
        :return: created events track
        """

        # Create events track object and fill it with provided events.
        events_track = cls(type, ticks_per_quarter_note)
        events_track._events = events

        return events_track

    def convert_to_notes(self):
        """
        Convert track's events to notes.

        :return: array of notes
        """

        # Create lists needed in conversion.
        notes_values = []
        events_pairs = self._pair_up_events()

        for event_pair in events_pairs:

            # Unpack event pair and save it in notes_values.
            start_time, delta_time, on_event, end_time, off_event = event_pair
            delta_time, pauses = self._trim_delta_time(delta_time)
            notes_values += pauses
            notes_values.append(
                [on_event.get_pitch(), delta_time, end_time - start_time]
            )

        # Trim durations and insert pauses in empty spaces.
        notes_values = EventsTrack._trim_durations(notes_values)
        notes_values = EventsTrack._fill_empty_spaces(notes_values)

        notes = []

        for pitch, delta_time, duration in notes_values:
            if self._type == TrackTypes.GUITAR_TRACK:
                notes.append(GuitarNote(pitch, delta_time, duration))
            else:
                notes.append(DrumsNote(pitch, delta_time, duration))

        return notes

    def write_bytes_to(self, destination):
        """
        Output track as bytes to destination.

        :param destination: MidiBytesIO object, destination for writing
        :return: -
        """

        # Write every event as bytes to destination.
        for event in self._events:
            event.write_to(destination)

    def _determine_type(self):
        """
        Determine whether it is guitar or drums track.

        :return: -
        """

        # Find first event in track's events and determine track type
        # based on whether it is drum note or not.
        for event in self._events:
            if event.is_drum_note():
                self._type = TrackTypes.DRUMS_TRACK
                break
            else:
                self._type = TrackTypes.GUITAR_TRACK
                break

    def _read_event(self, source):
        """
        Read bytes from source and create event object based on them.
        Append created event to instance array.

        :param source: MidiBytesIO objects which is source for reading
        :return: -
        """

        # Read delta time and status code byte from source.
        delta_time = source.read_vlq()
        status_code = source.read_byte()

        # Create new event object which type is based on previously read
        # status code.
        if self.MAX_MIDI_STATUS_CODE >= \
                status_code >= \
                EventsTrack.MIN_MIDI_STATUS_CODE:
            event = MidiEvent.from_bytes(delta_time, status_code, source)
        elif status_code == EventsTrack.META_STATUS_CODE:
            event = MetaEvent(delta_time, status_code, source)
        else:
            event = SysexEvent(delta_time, status_code, source)

        self._events.append(event)

    @staticmethod
    def _trim_durations(notes_values):
        """
        Trim chords notes to equal durations.

        :param notes_values: array of notes values
        :return: trimmed notes values
        """

        chord = []
        durations_in_chord = []

        for i in range(len(notes_values)):

            # If note is chord note (delta time = 0) append it to
            # current chord.
            if notes_values[i][EventsTrack.DELTA_TIME_INDEX] == 0:
                chord.append(i)
                durations_in_chord.append(
                    [notes_values[i][EventsTrack.DURATION_INDEX]]
                )

            # Else:
            else:

                # Set durations of all notes in chord to the same value
                # (smallest from all notes durations or trim it to match
                #  next note's delta time).
                notes_duration = min(
                    *durations_in_chord,
                    notes_values[i][EventsTrack.DELTA_TIME_INDEX]
                )
                for j in chord:
                    notes_values[j][EventsTrack.DURATION_INDEX] = \
                        notes_duration

            # Set chord to currently processed note index and durations to its
            # duration.
            chord = [i]
            durations_in_chord = [notes_values[i][EventsTrack.DURATION_INDEX]]

        return  notes_values

    def _trim_delta_time(self, delta_time):
        """
        Convert delta time to max possible time interval if it exceeds
        it and convert remaining time to pauses.

        :param delta_time: input interval
        :return: converted interval, list of pauses
        """

        # Return unmodified delta time and empty list of pauses if the interval
        # doesnt exceed set bounds.
        if delta_time <= self._max_time_interval:
            return delta_time, []

        pauses = []

        # Create first pause if it is necessary.
        first_pause_interval = delta_time % self._max_time_interval
        if first_pause_interval != 0:
            pauses.append(
                [
                    Note.PAUSE_PITCH,
                    first_pause_interval,
                    self._max_time_interval
                ]
            )

        # Create full pauses list.
        number_of_full_pauses = (delta_time - first_pause_interval) // \
                                self._max_time_interval - 1
        pauses += [
            [Note.PAUSE_PITCH, self._max_time_interval, self._max_time_interval]
        ] * number_of_full_pauses

        return self._max_time_interval, pauses

    def _pair_up_events(self):
        """
        Create on and off events pairs from events list.

        :return: list of paired up events
        """

        events_pairs = []
        if self._type == TrackTypes.GUITAR_TRACK:
            events_history = [-1] * EventsTrack.GUITAR_HISTORY_SIZE
        else:
            events_history = [-1] * EventsTrack.DRUMS_HISTORY_SIZE

        time = 0
        previous_time = 0
        i = 0

        # Pair up events and save them in events pairs list.
        for event in self._events:
            time += event.get_delta_time()
            if not event.is_note_event():

                # Skip loop iteration if event is not note event.
                continue

            if event.is_note_on():

                # Add start event to new event pair with its time and
                # delta time.
                events_history_index = self._get_pitch_event_history_index(
                    event.get_pitch()
                )
                events_pairs.append([time, time - previous_time, event])
                events_history[events_history_index] = i
                i += 1
                previous_time = time

            else:

                # Add close event and close time to previously opened event
                # for this pitch saved in events pairs.
                events_history_index = self._get_pitch_event_history_index(
                    event.get_pitch()
                )
                events_pairs[
                    events_history[events_history_index]
                ] += [time, event]

        return events_pairs

    def _get_pitch_event_history_index(self, pitch):
        """
        Get events history index of event with given pitch.

        :param pitch: event's pitch
        :return: events history index
        """

        if self._type == TrackTypes.GUITAR_TRACK:
            return pitch - GuitarNote.MIN_PITCH
        else:
            return DrumsNote.DRUMS_PITCH_LIST.index(pitch)

    @staticmethod
    def _fill_empty_spaces(notes_values):
        """
        Insert pauses into empty spaces between notes.

        :param notes_values: notes values
        :return: converted notes_values
        """

        pauses = []
        previous_duration = 0

        for i in range(len(notes_values)):

            # If there is space between notes save this index to
            # insert pause there later.
            if notes_values[i][EventsTrack.DELTA_TIME_INDEX] > \
                    previous_duration:

                pauses.append(
                    [
                        i,
                        previous_duration,
                        notes_values[i][EventsTrack.DELTA_TIME_INDEX] -
                        previous_duration
                    ]
                )

        pause_counter = 0

        for insertion_index, delta_time, duration in pauses:

            # In every previously saved place insert a pause.
            notes_values.insert(
                insertion_index,
                [Note.PAUSE_PITCH, delta_time, duration]
            )
            notes_values[insertion_index + 1][EventsTrack.DELTA_TIME_INDEX] = \
                duration
            pause_counter += 1

        return notes_values
