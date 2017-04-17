from ..tracks.NotesTrack import NotesTrack
from ..tracks.EventsTrack import EventsTrack
from ..tracks.TrackTypes import TrackTypes
from ..utilities.MidiBytesIO import MidiBytesIO

class MidiFile:
    """
    Midi file handler.
    """

    DEFAULT_HEADER_LENGTH = 6
    NOTES_WRAP = 50
    NOTES_FRAME_LENGTH = 100

    def __init__(self, file_path):
        file = open(file_path, "r")
        self._midi_bytes = MidiBytesIO(file.read())

    def get_notes_matrices(self):
        """
        Return midi bytes transformed to notes matrix.
        :return: notes matrix exported from file
        """

        # Read header, midi type, number of tracks and ticks_per_q_note.
        self._midi_bytes.read_header()
        header_length = self._midi_bytes.read_int()
        self._midi_bytes.read_short()
        number_of_tracks = self._midi_bytes.read_short()
        ticks_per_quarter_note = self._midi_bytes.read_short()
        self._midi_bytes.read(header_length - self.DEFAULT_HEADER_LENGTH)

        notes_matrices = []

        # Transform every read track intro notes matrix and append it to list.
        for i in range(number_of_tracks):
            self._midi_bytes.read_header()
            track_length = self._midi_bytes.read_int()
            events_track = EventsTrack.from_bytes(
                ticks_per_quarter_note, self._midi_bytes
            )
            notes = events_track.convert_to_notes()
            track_type = events_track.get_type()
            notes_track = NotesTrack.from_notes(
                track_type, ticks_per_quarter_note, notes
            )
            notes_matrices.append(
                notes_track.get_wrapped_notes_matrix(
                    self.NOTES_WRAP, self.NOTES_FRAME_LENGTH
                )
            )

        return notes_matrices