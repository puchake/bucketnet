from .Event import Event
from .EventTypes import EventTypes


class MetaEvent (Event):

    def __init__(self, delta_time, status_code, meta_type, length, data):
        super().__init__(delta_time, status_code, data)
        self._meta_type = meta_type
        self._length = length

    @property
    def type(self):
        return EventTypes.META_EVENT

    @property
    def meta_type(self):
        return self._meta_type

    @property
    def length(self):
        return self._length

    @property
    def is_end_of_track(self):
        return self._meta_type == 0x2F

    @property
    def is_note_on(self):
        return False

    @property
    def is_note_off(self):
        return False