from ..tracks.NotesTrack import NotesTrack
from ..tracks.EventsTrack import EventsTrack
from ..tracks.TrackTypes import TrackTypes
from ..utilities.MidiBytesIO import MidiBytesIO

import numpy as np


class NotesFile:
    """
    Notes file handler.
    """

    DEFAULT_MIDI_HEADER_LENGTH = 6
    DEFAULT_MIDI_TYPE = 1
    NUMBER_OF_TRACKS = 1

    def __init__(self, file_path):
        file = open(file_path, "rb")
        self._type = TrackTypes(np.fromfile(file, dtype=np.int32, count=1))
        self._ticks_per_quarter_note = np.fromfile(
            file, dtype=np.int32, count=1
        )
        self._notes_matrix = np.fromfile(file)

    def get_bytes(self):
        """
        Return notes file as bytes.
        :return: midi bytes
        """

        # Write midi header and track header.
        midi_bytes = MidiBytesIO(b'')
        midi_bytes.write_header(MidiBytesIO.HEADER_HEADER)
        midi_bytes.write_int(self.DEFAULT_MIDI_HEADER_LENGTH)
        midi_bytes.write_int(self.DEFAULT_MIDI_TYPE)
        midi_bytes.write_int(self.NUMBER_OF_TRACKS)
        midi_bytes.write_int(self._ticks_per_quarter_note)
        midi_bytes.write_header(MidiBytesIO.TRACK_HEADER)

        # Create notes track, convert it to events and convert them to bytes
        # using events track.
        notes_track = NotesTrack.from_matrix(
            self._type, self._ticks_per_quarter_note, self._notes_matrix
        )
        track_events = notes_track.convert_to_events()
        events_track = EventsTrack.from_events(self._type, self._ticks_per_quarter_note, track_events)
        events_track.write_bytes_to(midi_bytes)

        # Return all bytes.
        midi_bytes.seek(0)
        return midi_bytes.read()