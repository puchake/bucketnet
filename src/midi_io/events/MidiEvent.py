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

    def __init__(self, delta_time, status_code, data):
        super().__init__(delta_time, status_code, data)

    def get_type(self):
        return EventTypes.MIDI_EVENT

    def is_note_on(self):
        """
        Check if midi event is note-on event.

        :return: check result
        """

        return self._get_midi_type() == MidiEventTypes.NOTE_ON

    def is_note_off(self):
        """
        Check if midi event is note-off event.

        :return: check result
        """

        return self._get_midi_type() == MidiEventTypes.NOTE_OFF or \
               (self._get_midi_type() == MidiEventTypes.NOTE_ON and
                self._get_velocity() == MidiEventTypes.NOTE_OFF_VELOCITY)

    def is_drums_event(self):
        """
        Check if midi event is related to percussion channel.

        :return: check result
        """

        return self._get_channel() == MidiEvent.DRUMS_CHANNEL

    def write_to(self, destination):
        destination.write_vlq(self._delta_time)
        destination.write_byte(self._status_code)
        destination.write(self._data)

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

    def _get_pitch(self):
        """
        Get note's pitch number from data byte array.

        :return: Get pitch number
        """

        return self._data[MidiEvent.NOTE_EVENT_PITCH]

    def _get_velocity(self):
        """
        Get note's velocity from data array.

        :return: note's velocity
        """

        return self._data[MidiEvent.NOTE_EVENT_VELOCITY]