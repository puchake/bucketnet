from .Event import Event
from .EventTypes import EventTypes


class SysexEvent (Event):
    """
    Class representing system exclusive events.
    """

    def __init__(self, delta_time, status_code, length, data):
        super().__init__(delta_time, status_code, data)
        self._length = length

    def get_type(self):
        return EventTypes.SYSEX_EVENT

    def write_to(self, destination):
        destination.write_vlq(self._delta_time)
        destination.write_byte(self._status_code)
        destination.write_vlq(self._length)
        destination.write(self._data)