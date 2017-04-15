from abc import ABC, abstractmethod, abstractclassmethod

import numpy as np


class Note (ABC):
    """
    Abstract class representing single note.
    """

    # Special value for pitch which indicates that this note is in fact pause.
    PAUSE_PITCH = -1

    # Constant lengths of 1/0 vectors representing time.
    # 8 for full, half, quarter, 1/8, 1/16, 1/32, 1/64 or 0 note
    # 3 for note modifier - normal, dotted, triplet note
    TIME_LENGTH_VECTOR_LENGTH = 8
    TIME_TYPE_VECTOR_LENGTH = 3
    TIME_VECTOR_LENGTH = TIME_LENGTH_VECTOR_LENGTH + TIME_TYPE_VECTOR_LENGTH

    # Indices for accessing POSSIBLE_TIMINGS search results in
    # time <-> vector conversion.
    TIME_INDEX_TYPE_PART = 0
    TIME_INDEX_LENGTH_PART = 1

    # Array used to find closest, allowed matching time value
    # in time conversion.
    POSSIBLE_TIMINGS = (
        np.tile(np.append([0], 2.0 ** np.arange(7)), (3, 1)) *
        [[3.0], [2.0], [4.5]]
    )

    def __init__(self, type, pitch, delta_time, duration):
        self._type = type
        self._pitch = pitch
        self._delta_time = delta_time
        self._duration = duration

    def get_type(self):
        """
        Get note's type.

        :return: note's type
        """

        return self._type

    def get_pitch(self):
        """
        Get note's pitch.

        :return: note's pitch
        """

        return self._pitch

    def get_delta_time(self):
        """
        Get note's delta time.

        :return: note's delta time
        """

        return self._delta_time

    def get_duration(self):
        """
        Get note's duration.

        :return: note's duration
        """

        return self._duration

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

        :return: 1/0 pitch vector
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

    def _convert_delta_time_to_vector(self):
        """
        Convert note's delta_time to 1/0 vector.

        :return: 1/0 delta time vector
        """

        return Note._convert_time_to_vector(self._delta_time)

    def _convert_vector_to_delta_time(self, vector):
        """
        Convert

        :param vector: numpy vector which contains delta time data
        :return:
        """

        self._delta_time = Note._convert_vector_to_time(vector)

    def _convert_duration_to_vector(self):
        """
        Convert note's duration to 1/0 vector.

        :return: 1/0 duration vector
        """

        return Note._convert_time_to_vector(self._duration)

    def _convert_vector_to_duration(self, vector):
        """
        Convert

        :param vector: numpy vector which contains duration data
        :return:
        """

        self._duration = Note._convert_vector_to_time(vector)

    @staticmethod
    def _convert_time_to_vector(time):
        """
        Convert time value to 1/0 vector.

        :param time: time value to convert
        :return: converted time vector
        """

        # Get closest time value index from POSSIBLE_TIMINGS.
        time_index = np.unravel_index(
            np.argmin(np.absolute(Note.POSSIBLE_TIMINGS - time)),
            Note.POSSIBLE_TIMINGS.shape
        )

        # Create type and length vectors.
        time_type = np.zeros([Note.TIME_TYPE_VECTOR_LENGTH, ])
        time_length = np.zeros([Note.TIME_LENGTH_VECTOR_LENGTH, ])

        # Save 1 on position saved in index.
        time_type[time_index[Note.TIME_INDEX_TYPE_PART]] = 1.0
        time_length[time_index[Note.TIME_INDEX_LENGTH_PART]] = 1.0

        # Return connected length and type vectors.
        return np.append(time_length, time_type)

    @staticmethod
    def _convert_vector_to_time(vector):
        """
        Convert 1/0 vector to time value.

        :param vector: vector with time data inside it
        :return: converted time value
        """

        # Determine POSSIBLE_TIMINGS indices.
        time_type_index = np.argmax(vector[Note.TIME_LENGTH_VECTOR_LENGTH:])
        time_length_index = np.argmax(vector[:Note.TIME_LENGTH_VECTOR_LENGTH])

        # Return POSSIBLE_TIMINGS value pointed by indices.
        return Note.POSSIBLE_TIMINGS[time_type_index, time_length_index]
