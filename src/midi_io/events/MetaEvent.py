from .Event import Event
from .EventTypes import EventTypes


class MetaEvent (Event):
    """
    Class representing meta event.
    """

    # Constant meta type indicating end-of-track event.
    END_OF_TRACK_META_TYPE = 0x2F

    def __init__(self, delta_time, status_code, meta_type, length, data):
        super().__init__(delta_time, status_code, data)
        self._meta_type = meta_type
        self._length = length

    def get_type(self):
        return EventTypes.META_EVENT

    def is_end_of_track(self):
        """
        Check if event is end-of-track-event.

        :return: check result
        """
        return self._meta_type == MetaEvent.END_OF_TRACK_META_TYPE

    def write_to(self, destination):
        destination.write_vlq(self._delta_time)
        destination.write_byte(self._status_code)
        destination.write_byte(self._meta_type)
        destination.write_vlq(self._length)
        destination.write(self._data)