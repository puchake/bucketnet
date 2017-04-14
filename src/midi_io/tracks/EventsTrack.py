from .Track import Track
from .TrackTypes import TrackTypes
from ..events.MidiEvent import MidiEvent
from ..events.MetaEvent import MetaEvent
from ..events.SysexEvent import SysexEvent


class EventsTrack (Track):
    """
    Class representing track composed of events.
    """

    # Constants used to determine event type based on read status code.
    MIN_MIDI_STATUS_CODE = 0x80
    MAX_MIDI_STATUS_CODE = 0xEF
    META_STATUS_CODE = 0xFF

    def __init__(self, type, ticks_per_quarter_note):
        super().__init__(type, ticks_per_quarter_note)
        self._events = []

    @classmethod
    def from_bytes(cls, ticks_per_quarter_note, source):
        """
        Constructor overload for creating events track from raw midi bytes.

        :param ticks_per_quarter_note: midi ticks per quarter note
        :param source: MidiBytesIO object, source for reading
        :return: created events track
        """

        events_track = cls(TrackTypes.NOT_DETERMINED, ticks_per_quarter_note)

        # TODO

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

        events_track = cls(type, ticks_per_quarter_note)

        # TODO

        return events_track


    def convert_to_notes(self):
        """
        Convert track's events to notes.

        :return: array of notes
        """

        # TODO

        pass

    def _determine_type(self):
        """
        Determine whenever it is guitar or drums track.

        :return: -
        """

        # TODO

        pass

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