from src.midi_io.utilities.EventUtilities import EventUtilities
from src.midi_io.utilities.MidiBytesIO import MidiBytesIO
from src.midi_io.events.MidiEvent import MidiEvent
from src.midi_io.events.MetaEvent import MetaEvent
from src.midi_io.events.SysexEvent import SysexEvent

import unittest


class EventUtilitiesTestCase(unittest.TestCase):

    def test_read_event_midi_event(self):

        # Arrange
        event_bytes = b'\x0A\x80\x2F\x00'
        source = MidiBytesIO(event_bytes)

        # Act
        event = EventUtilities.read_event(source)

        # Assert
        self.assertTrue(event.is_note_off())

    def test_read_event_meta_event(self):

        # Arrange
        event_bytes = b'\x0A\xFF\x2F\x00'
        source = MidiBytesIO(event_bytes)

        # Act
        event = EventUtilities.read_event(source)

        # Assert
        self.assertTrue(event.is_end_of_track())

    def test_read_event_sysex_event(self):

        # Arrange
        event_bytes = b'\x0A\xF0\x01\xF7'
        source = MidiBytesIO(event_bytes)
        destination = MidiBytesIO(b'')

        # Act
        event = EventUtilities.read_event(source)

        # Assert
        event.write_to(destination)
        self.assertTrue(destination.getbuffer(), event_bytes)

    def test_write_event_midi_event(self):

        # Arrange
        event = MidiEvent(0xFFFFFFF, 0x90, b'\x04\x00')
        expected_event_bytes = b'\xFF\xFF\xFF\x7F\x90\x04\x00'
        destination = MidiBytesIO(b'')

        # Act
        event.write_to(destination)

        # Assert
        self.assertEqual(destination.getbuffer(), expected_event_bytes)

    def test_write_event_meta_event(self):

        # Arrange
        event = MetaEvent(0xFFC3F8A, 0xFF, 0x2F, 0x00, b'')
        expected_event_bytes = b'\xFF\xF0\xFF\x0A\xFF\x2F\x00'
        destination = MidiBytesIO(b'')

        # Act
        event.write_to(destination)

        # Assert
        self.assertEqual(destination.getbuffer(), expected_event_bytes)

    def test_write_event_sysex_event(self):

        # Arrange
        event = SysexEvent(0xFFC3F8A, 0xF0, 0x04, b'\xAA\xBB\xCC\xF7')
        expected_event_bytes = b'\xFF\xF0\xFF\x0A\xF0\x04\xAA\xBB\xCC\xF7'
        destination = MidiBytesIO(b'')

        # Act
        event.write_to(destination)

        # Assert
        self.assertEqual(destination.getbuffer(), expected_event_bytes)


if __name__ == '__main__':
    unittest.main()
