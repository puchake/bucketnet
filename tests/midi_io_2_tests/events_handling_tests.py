import src.midi_io.events_handling as events_handling

import unittest
from io import BytesIO


class EventsHandlingTestCase (unittest.TestCase):

    def test_read_vlq_1_byte(self):

        # Arrange
        vlq_bytes = b'\x0A'
        source = BytesIO(vlq_bytes)

        # Act
        value = events_handling.read_vlq(source)

        # Assert
        self.assertEqual(value, 0x0A)

    def test_read_vlq_2_byte(self):

        # Arrange
        vlq_bytes = b'\xF3\x0A'
        source = BytesIO(vlq_bytes)

        # Act
        value = events_handling.read_vlq(source)

        # Assert
        self.assertEqual(value, 0x398A)

    def test_read_vlq_3_byte(self):

        # Arrange
        vlq_bytes = b'\xF8\x87\x0C'
        source = BytesIO(vlq_bytes)

        # Act
        value = events_handling.read_vlq(source)

        # Assert
        self.assertEqual(value, 0x1E038C)

    def test_read_vlq_4_byte(self):

        # Arrange
        vlq_bytes = b'\xFF\xFF\xFF\x7F'
        source = BytesIO(vlq_bytes)

        # Act
        value = events_handling.read_vlq(source)

        # Assert
        self.assertEqual(value, 0xFFFFFFF)

    def test_write_vlq_1_byte(self):

        # Arrange
        vlq_value = 0x0A
        destination = BytesIO(b'')

        # Act
        events_handling.write_vlq(destination, vlq_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\x0A')

    def test_write_vlq_2_byte(self):

        # Arrange
        vlq_value = 0x398A
        destination = BytesIO(b'')

        # Act
        events_handling.write_vlq(destination, vlq_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\xF3\x0A')

    def test_write_vlq_3_byte(self):

        # Arrange
        vlq_value = 0x1E038C
        destination = BytesIO(b'')

        # Act
        events_handling.write_vlq(destination, vlq_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\xF8\x87\x0C')

    def test_write_vlq_4_byte(self):

        # Arrange
        vlq_value = 0xFFFFFFF
        destination = BytesIO(b'')

        # Act
        events_handling.write_vlq(destination, vlq_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\xFF\xFF\xFF\x7F')

    def test_read_event_1_event(self):

        # Arrange
        source_bytes = b'\x00\xFF\x2F\x00'
        source = BytesIO(source_bytes)

        # Act
        event = events_handling.read_event(source)

        # Assert
        self.assertEqual(event.delta_time, 0)
        self.assertEqual(event.status_code, 0xFF)
        self.assertEqual(event.meta_type, 0x2F)
        self.assertEqual(event.length, 0x00)

    def test_read_event_2_events(self):

        # Arrange
        source_bytes = b'\x0A\x80\x00\x00\x00\xFF\x2F\x00'
        source = BytesIO(source_bytes)

        # Act
        event_1 = events_handling.read_event(source)
        event_2 = events_handling.read_event(source)

        # Assert
        self.assertEqual(event_1.delta_time, 0x0A)
        self.assertEqual(event_1.status_code, 0x80)
        self.assertEqual(event_1.meta_type, None)
        self.assertEqual(event_1.length, None)
        self.assertEqual(event_1.data, b'\x00\x00')

        self.assertEqual(event_2.delta_time, 0)
        self.assertEqual(event_2.status_code, 0xFF)
        self.assertEqual(event_2.meta_type, 0x2F)
        self.assertEqual(event_2.length, 0x00)
        self.assertEqual(event_2.data, b'')

    def test_write_event_1_event(self):

        # Arrange
        event = events_handling.Event(
            events_handling.META_EVENT, 0x00, 0xFF, 0x2F, 0x00, b''
        )
        destination = BytesIO(b'')

        # Act
        events_handling.write_event(destination, event)

        # Assert
        self.assertEqual(
            destination.getbuffer(), b'\x00\xFF\x2F\x00'
        )

    def test_write_event_2_events(self):

        # Arrange
        event_1 = events_handling.Event(
            events_handling.MIDI_EVENT, 0x0A, 0x80, None, None, b'\x00\x00'
        )
        event_2 = events_handling.Event(
            events_handling.META_EVENT, 0x00, 0xFF, 0x2F, 0x00, b''
        )
        destination = BytesIO(b'')

        # Act
        events_handling.write_event(destination, event_1)
        events_handling.write_event(destination, event_2)

        # Assert
        self.assertEqual(
            destination.getbuffer(), b'\x0A\x80\x00\x00\x00\xFF\x2F\x00'
        )

    def test_is_end_of_track_true_case(self):

        # Arrange
        event = events_handling.Event(
            events_handling.META_EVENT, 0, 0xFF, 0x2F, 0x00, b''
        )

        # Act
        result = events_handling.is_end_of_track(event)

        # Assert
        self.assertTrue(result)

    def test_is_end_of_track_false_case(self):

        # Arrange
        event = events_handling.Event(
            events_handling.META_EVENT, 0, 0xFF, 0x3F, 0x00, b''
        )

        # Act
        result = events_handling.is_end_of_track(event)

        # Assert
        self.assertFalse(result)

    def test_is_note_event_true_case(self):

        # Arrange
        event = events_handling.Event(
            events_handling.MIDI_EVENT, 0, 0x83, None, None, b'\x00\x00'
        )

        # Act
        result = events_handling.is_note_event(event)

        # Assert
        self.assertTrue(result)

    def test_is_note_event_false_case(self):

        # Arrange
        event = events_handling.Event(
            events_handling.MIDI_EVENT, 0, 0xA0, None, None, b'\x00\x00'
        )

        # Act
        result = events_handling.is_note_event(event)

        # Assert
        self.assertFalse(result)

    def test_is_note_on_true_case(self):

        # Arrange
        event = events_handling.Event(
            events_handling.MIDI_EVENT, 0, 0x93, None, None, b'\x07\x08'
        )

        # Act
        result = events_handling.is_note_on(event)

        # Assert
        self.assertTrue(result)

    def test_is_note_on_false_case(self):

        # Arrange
        event = events_handling.Event(
            events_handling.MIDI_EVENT, 0, 0x83, None, None, b'\x07\x00'
        )

        # Act
        result = events_handling.is_note_on(event)

        # Assert
        self.assertFalse(result)

    def test_is_note_off_true_case(self):

        # Arrange
        event = events_handling.Event(
            events_handling.MIDI_EVENT, 0, 0x80, None, None, b'\x00\x00'
        )

        # Act
        result = events_handling.is_note_off(event)

        # Assert
        self.assertTrue(result)

    def test_is_note_off_false_case(self):

        # Arrange
        event = events_handling.Event(
            events_handling.MIDI_EVENT, 0, 0x93, None, None, b'\x00\x05'
        )

        # Act
        result = events_handling.is_note_off(event)

        # Assert
        self.assertFalse(result)

    def test_is_drums_event_true_case(self):

        # Arrange
        event = events_handling.Event(
            events_handling.MIDI_EVENT, 0, 0x89, None, None, b'\x00\x05'
        )

        # Act
        result = events_handling.is_drums_event(event)

        # Assert
        self.assertTrue(result)

    def test_is_drums_event_false_case(self):

        # Arrange
        event = events_handling.Event(
            events_handling.MIDI_EVENT, 0, 0x83, None, None, b'\x00\x05'
        )

        # Act
        result = events_handling.is_drums_event(event)

        # Assert
        self.assertFalse(result)

    def test_is_events_list_empty_true_case(self):

        # Arrange
        events = [
            events_handling.Event(
                events_handling.META_EVENT, 0, 0xFF, 0x2F, 0x00, b''
            ),
            events_handling.Event(
                events_handling.META_EVENT, 0, 0xFF, 0x2F, 0x00, b''
            ),
            events_handling.Event(
                events_handling.SYSEX_EVENT, 0, 0xF0, None, 0x00, b''
            )
        ]

        # Act
        result = events_handling.is_events_list_empty(events)

        # Assert
        self.assertTrue(result)

    def test_is_events_list_empty_false_case(self):

        # Arrange
        events = [
            events_handling.Event(
                events_handling.META_EVENT, 0, 0xFF, 0x2F, 0x00, b''
            ),
            events_handling.Event(
                events_handling.META_EVENT, 0, 0xFF, 0x2F, 0x00, b''
            ),
            events_handling.Event(
                events_handling.SYSEX_EVENT, 0, 0xF0, None, 0x00, b''
            ),
            events_handling.Event(
                events_handling.MIDI_EVENT, 0, 0x83, None, None, b'\x00\x05'
            )
        ]

        # Act
        result = events_handling.is_events_list_empty(events)

        # Assert
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
