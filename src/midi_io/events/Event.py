from abc import ABC, abstractproperty


class Event (ABC):

    def __init__(self, delta_time, status_code, data):
        self._delta_time = delta_time
        self._status_code = status_code
        self._data = data

    @abstractproperty
    def type(self):
        pass

    @property
    def delta_time(self):
        return self._delta_time

    @property
    def status_code(self):
        return self._status_code

    @property
    def data(self):
        return self._data

    @abstractproperty
    def is_end_of_track(self):
        pass

    @abstractproperty
    def is_note_on(self):
        pass

    @abstractproperty
    def is_note_off(self):
        pass