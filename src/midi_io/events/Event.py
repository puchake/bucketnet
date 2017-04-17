from abc import ABC, abstractmethod


class Event (ABC):
    """
    Abstract class representing midi event.
    """

    def __init__(self, delta_time, status_code):
        self._delta_time = delta_time
        self._status_code = status_code
        self._data = b''

    @abstractmethod
    def get_type(self):
        """
        Get event type.

        :return: one of EventTypes values
        """

        pass

    def get_delta_time(self):
        """
        Get delta time value.

        :return: event's delta time value.
        """

        return self._delta_time

    def is_note_on(self):
        """
        Check if midi event is note-on event.

        :return: check result
        """

        return False

    def is_note_off(self):
        """
        Check if midi event is note-off event.

        :return: check result
        """

        return False

    def is_drums_event(self):
        """
        Check if midi event is related to percussion channel.

        :return: check result
        """

        return False

    def is_end_of_track(self):
        """
        Check if event is end-of-track-event.

        :return: check result
        """

        return False

    @abstractmethod
    def write_to(self, destination):
        """
        Output event to destination as bytes in event type specific format.

        :param destination: MidiBytesIO object which is writing destination
        :return: -
        """

        pass
