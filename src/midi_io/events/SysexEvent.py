from .Event import Event
from .EventTypes import EventTypes


class SysexEvent (Event):

    def __init__(self, delta_time, status_code, length, data):
        super().__init__(delta_time, status_code, data)
        self._length = length

    @property
    def type(self):
        return EventTypes.SYSEX_EVENT

    @property
    def length(self):
        return self._length

    @property
    def is_end_of_track(self):
        return False

    @property
    def is_note_on(self):
        return False

    @property
    def is_note_off(self):
        return False
