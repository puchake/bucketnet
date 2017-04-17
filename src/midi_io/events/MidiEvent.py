from .Event import Event
from .EventTypes import EventTypes
from .MidiEventTypes import MidiEventTypes


class MidiEvent (Event):
    """
    Class representing midi event.
    """

    # Masks for extracting midi type and channel from status code.
    MIDI_TYPE_MASK = 0b11110000
    CHANNEL_MASK = 0b00001111

    # Constant channel used for percussion instruments.
    DRUMS_CHANNEL = 0x09

    # Indices for note event parameters in data byte array.
    NOTE_EVENT_PITCH = 0
    NOTE_EVENT_VELOCITY = 1

    # Special note-on event velocity meaning that this event turns note off.
    NOTE_OFF_VELOCITY = 0

    # midi-event-type -> number-of-data-bytes dictionary
    MIDI_EVENT_LENGTHS = {
        MidiEventTypes.NOTE_OFF: 2,
        MidiEventTypes.NOTE_ON: 2,
        MidiEventTypes.POLYPHONIC_PRESSURE: 2,
        MidiEventTypes.CONTROLLER: 2,
        MidiEventTypes.PROGRAM_CHANGE: 1,
        MidiEventTypes.CHANNEL_PRESSURE: 1,
        MidiEventTypes.PITCH_BEND: 2
    }

    def __init__(self, delta_time, status_code):
        super().__init__(delta_time, status_code)

    @classmethod
    def from_bytes(cls, delta_time, status_code, source):
        """
        Initialize new midi event with delta_time and status_code.
        Read remaining data from source.

        :param delta_time: event's delta_time
        :param status_code: event's status_code
        :param source: MidiBytesIO object, source for reading
        """

        midi_event = cls(delta_time, status_code)
        data_length = MidiEvent.MIDI_EVENT_LENGTHS[midi_event._get_midi_type()]
        midi_event._data = source.read(data_length)
        return midi_event

    @classmethod
    def from_values(cls, delta_time, status_code, data):
        """
        Initialize new midi event with delta_time and status_code.
        Save input data as bytes inside.

        :param delta_time: event's delta_time
        :param status_code: event's status_code
        :param data: array of event's data values
        """

        midi_event = cls(delta_time, status_code)
        midi_event._data = bytes(data)
        return midi_event

    def get_type(self):
        return EventTypes.MIDI_EVENT

    def is_note_on(self):
        return self._get_midi_type() == MidiEventTypes.NOTE_ON and \
               self.get_velocity() != MidiEventTypes.NOTE_OFF_VELOCITY

    def is_note_off(self):
        return self._get_midi_type() == MidiEventTypes.NOTE_OFF or \
               (self._get_midi_type() == MidiEventTypes.NOTE_ON and
                self.get_velocity() == MidiEventTypes.NOTE_OFF_VELOCITY)

    def is_drums_event(self):
        return self._get_channel() == MidiEvent.DRUMS_CHANNEL

    def write_to(self, destination):
        destination.write_vlq(self._delta_time)
        destination.write_byte(self._status_code)
        destination.write(self._data)

    def get_pitch(self):
        """
        Get note's pitch number from data byte array.

        :return: Get pitch number
        """

        return self._data[MidiEvent.NOTE_EVENT_PITCH]

    def get_velocity(self):
        """
        Get note's velocity from data array.

        :return: note's velocity
        """

        return self._data[MidiEvent.NOTE_EVENT_VELOCITY]

    def _get_midi_type(self):
        """
        Extract event's midi type from status code.

        :return: extracted midi type as enum value
        """

        return MidiEventTypes(self._status_code & MidiEvent.MIDI_TYPE_MASK)

    def _get_channel(self):
        """
        Extract event's channel from status code.

        :return: extracted channel
        """

        return self._status_code & MidiEvent.CHANNEL_MASK
