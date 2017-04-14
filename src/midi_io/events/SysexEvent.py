from .Event import Event
from .EventTypes import EventTypes


class SysexEvent (Event):
    """
    Class representing system exclusive events.
    """

    def __init__(self, delta_time, status_code, source):
        """
        Initialize new system exclusive event with delta_time and status_code.
        Read remaining data from source.

        :param delta_time: event's delta_time
        :param status_code: event's status_code
        :param source: MidiBytesIO object, source for reading
        """

        super().__init__(delta_time, status_code)
        self._length = source.read_vlq()
        self._data = source.read(self._length)

    def get_type(self):
        return EventTypes.SYSEX_EVENT

    def write_to(self, destination):
        destination.write_vlq(self._delta_time)
        destination.write_byte(self._status_code)
        destination.write_vlq(self._length)
        destination.write(self._data)
