from .Event import Event
from .EventTypes import EventTypes
from .MidiEventTypes import MidiEventTypes


class MidiEvent (Event):

    MIDI_TYPE_MASK = 0b11110000
    CHANNEL_MASK = 0b00001111

    def __init__(self, delta_time, status_code, data):
        super().__init__(delta_time, status_code, data)

    @property
    def type(self):
        return EventTypes.MIDI_EVENT

    @property
    def midi_type(self):
        return self._status_code & MidiEvent.MIDI_TYPE_MASK

    @property
    def channel(self):
        return self._status_code & MidiEvent.CHANNEL_MASK

    @property
    def is_end_of_track(self):
        return False

    @property
    def is_note_on(self):
        return self.midi_type == MidiEventTypes.NOTE_ON

    @property
    def is_note_off(self):
        return self.midi_type == MidiEventTypes.NOTE_OFF