from ..notes.GuitarNote import GuitarNote
from ..notes.DrumsNote import DrumsNote
from ..events.MidiEvent import MidiEvent


class NoteEventConverter:
    """
    Utilities class which can convert notes to midi events and
    other way around.
    """

    @staticmethod
    def convert_note_to_events(note):
        """
        Converts note to on and off events pair.

        :param note: note to convert
        :return: pair of events
        """

        # TODO

        pass

    @staticmethod
    def convert_events_pair_to_note(on_event, off_event):
        """
        Convert pair of events to note.

        :param on_event: note on midi event
        :param off_event: respective note off midi event
        :return: note described by provided pair of events
        """

        # TODO

        pass
