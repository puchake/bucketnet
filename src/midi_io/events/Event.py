from abc import ABC, abstractmethod


class Event (ABC):
    """
    Abstract class representing midi event.
    """

    def __init__(self, delta_time, status_code, data):
        self._delta_time = delta_time
        self._status_code = status_code
        self._data = data

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

        :return: event delta time value.
        """

        return self._delta_time

    @abstractmethod
    def write_to(self, destination):
        """
        Output event to destination as bytes in event type specific format.

        :param destination: MidiBytesIO object which is writing destination
        :return: -
        """

        pass