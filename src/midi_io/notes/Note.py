from abc import ABC, abstractmethod, abstractclassmethod


class Note (ABC):
    """
    Abstract class representing single note.
    """

    # Constant length of 1/0 vector representation of time.
    # 8 for full, half, quarter, 1/8, 1/16, 1/32, 1/64 or 0 note
    # 3 for note modifier - normal, dotted, triplet note
    TIME_VECTOR_LENGTH = 8 + 3

    def __init__(self, type, pitch, delta_time, duration):
        self._type = type
        self._pitch = pitch
        self._delta_time = delta_time
        self._duration = duration

    @abstractmethod
    def convert_to_vector(self):
        """
        Convert note to 1/0 numpy vector.

        :return: note converted to vector
        """

        pass

    @abstractmethod
    def _convert_pitch_to_vector(self):
        """
        Convert note's pitch to 1/0 vector.

        :return: -
        """

        pass

    @abstractmethod
    def _convert_vector_to_pitch(self, vector):
        """
        Convert

        :param vector: numpy vector which contains pitch data
        :return:
        """

        pass

    @classmethod
    def _convert_time_to_vector(cls, time):
        """
        Convert time value to 1/0 vector.

        :param time: time value to convert
        :return: converted time value
        """

        # TODO

        pass

    @classmethod
    def _convert_vector_to_time(cls, time):

        # TODO

        pass
