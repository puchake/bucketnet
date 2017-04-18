import midi_io.events_handling as events_handling
import midi_io.notes_handling as notes_handling
import midi_io.track_conversion as track_conversion

import unittest


class TrackConversionTestCase (unittest.TestCase):

    def test_get_event_note_type_guitar_event(self):

        # Arrange
        event = events_handling.Event(
            events_handling.MIDI_EVENT, 0x00, 0x80, None, None, b'\x00\x00'
        )
        expected_note_type = notes_handling.GUITAR_NOTE

        # Act
        note_type = track_conversion.get_event_note_type(event)

        # Assert
        self.assertEqual(note_type, expected_note_type)

    def test_get_event_note_type_drums_event(self):

        # Arrange
        event = events_handling.Event(
            events_handling.MIDI_EVENT, 0x00, 0x89, None, None, b'\x00\x00'
        )
        expected_note_type = notes_handling.DRUMS_NOTE

        # Act
        note_type = track_conversion.get_event_note_type(event)

        # Assert
        self.assertEqual(note_type, expected_note_type)

    def test_pair_up_events(self):

        # Arrange
        event_1_start = events_handling.Event(
            events_handling.MIDI_EVENT, 0x00, 0x90, None, None, b'\x0A\x0A'
        )
        event_1_stop = events_handling.Event(
            events_handling.MIDI_EVENT, 0x20, 0x80, None, None, b'\x0A\x0A'
        )
        event_2_start = events_handling.Event(
            events_handling.MIDI_EVENT, 0x30, 0x90, None, None, b'\x10\x0A'
        )
        event_2_stop = events_handling.Event(
            events_handling.MIDI_EVENT, 0x30, 0x80, None, None, b'\x10\x00'
        )
        events = [event_1_start, event_2_start, event_1_stop, event_2_stop] * 3
        expected_events_pairs = [
            [0x00, 0x00, 0x0A, 0x50],
            [0x30, 0x30, 0x10, 0x80],
            [0x80, 0x50, 0x0A, 0xD0],
            [0xB0, 0x30, 0x10, 0x100],
            [0x100, 0x50, 0x0A, 0x150],
            [0x130, 0x30, 0x10, 0x180]
        ]

        # Act
        events_pairs = track_conversion.pair_up_events(events)

        # Assert
        self.assertEqual(events_pairs, expected_events_pairs)

    def test_trim_delta_time_delta_time_less_than_max_time_interval(self):

        # Arrange
        max_time_interval = 960
        delta_time = 480

        # Act
        trimmed_delta_time, pauses = track_conversion.trim_delta_time(
            delta_time, max_time_interval
        )

        # Assert
        self.assertEqual(trimmed_delta_time, delta_time)
        self.assertEqual(pauses, [])

    def test_trim_delta_time_delta_time_more_than_max_time_interval(self):

        # Arrange
        max_time_interval = 960
        delta_time = 1922
        expected_delta_time = 2
        expected_last_pause = [
            None, notes_handling.PAUSE_PITCH,
            max_time_interval, delta_time % max_time_interval
        ]
        expected_full_pause = [
            None, notes_handling.PAUSE_PITCH,
            max_time_interval, max_time_interval
        ]
        expected_pauses = [expected_full_pause] * 1 + [expected_last_pause]

        # Act
        trimmed_delta_time, pauses = track_conversion.trim_delta_time(
            delta_time, max_time_interval
        )

        # Assert
        self.assertEqual(trimmed_delta_time, expected_delta_time)
        self.assertEqual(pauses, expected_pauses)

    def test_trim_delta_time_delta_time_is_multiple_max_time_interval(self):

        # Arrange
        max_time_interval = 960
        delta_time = 2880
        expected_delta_time = 960
        expected_full_pause = [
            None, notes_handling.PAUSE_PITCH,
            max_time_interval, max_time_interval
        ]
        expected_pauses = [expected_full_pause] * 2

        # Act
        trimmed_delta_time, pauses = track_conversion.trim_delta_time(
            delta_time, max_time_interval
        )

        # Assert
        self.assertEqual(trimmed_delta_time, expected_delta_time)
        self.assertEqual(pauses, expected_pauses)

    def test_trim_chords_durations_let_ring_notes(self):

        # Arrange
        notes_values = [
            [None, 20, 24, 192], [None, 20, 48, 192],
            [None, 20, 96, 192], [None, 20, 192, 192],
        ]
        expected_notes_values = [
            [None, 20, 24, 48], [None, 20, 48, 96],
            [None, 20, 96, 192], [None, 20, 192, 192],
        ]

        # Act
        track_conversion.trim_chords_durations(notes_values)

        # Assert
        self.assertEqual(notes_values, expected_notes_values)

    def test_trim_chords_durations_let_ring_chord(self):

        # Arrange
        notes_values = [
            [None, 20, 24, 192], [None, 20, 0, 192],
            [None, 20, 0, 192], [None, 20, 48, 192],
        ]
        expected_notes_values = [
            [None, 20, 24, 48], [None, 20, 0, 48],
            [None, 20, 0, 48], [None, 20, 48, 192],
        ]

        # Act
        track_conversion.trim_chords_durations(notes_values)

        # Assert
        self.assertEqual(notes_values, expected_notes_values)

    def test_trim_chords_durations_chord_shorter_than_next_delta_time(self):

        # Arrange
        notes_values = [
            [None, 20, 24, 24], [None, 20, 0, 192],
            [None, 20, 0, 192], [None, 20, 48, 192],
        ]
        expected_notes_values = [
            [None, 20, 24, 24], [None, 20, 0, 24],
            [None, 20, 0, 24], [None, 20, 48, 192],
        ]

        # Act
        track_conversion.trim_chords_durations(notes_values)

        # Assert
        self.assertEqual(notes_values, expected_notes_values)

    def test_fill_empty_spaces_between_notes(self):

        # Arrange
        notes_values = [
            [None, 20, 24, 24], [None, 20, 0, 24],
            [None, 20, 0, 24], [None, 20, 48, 192],
        ]
        expected_notes_values = [
            [None, -1, 0, 24], [None, 20, 24, 24],
            [None, 20, 0, 24], [None, 20, 0, 24],
            [None, -1, 24, 24], [None, 20, 24, 192],
        ]

        # Act
        track_conversion.fill_empty_spaces_between_notes(notes_values)

        # Assert
        self.assertEqual(notes_values, expected_notes_values)

    def test_convert_events_to_notes(self):

        # Arrange
        meta_event = events_handling.Event(
            events_handling.META_EVENT, 0x20, 0xFF, 0x2F, 0x00, b''
        )
        event_1_start = events_handling.Event(
            events_handling.MIDI_EVENT, 0x10, 0x90, None, None, b'\x20\x40'
        )
        event_1_stop = events_handling.Event(
            events_handling.MIDI_EVENT, 0x30, 0x80, None, None, b'\x20\x00'
        )
        event_2_start = events_handling.Event(
            events_handling.MIDI_EVENT, 0x10, 0x90, None, None, b'\x30\x40'
        )
        event_2_stop = events_handling.Event(
            events_handling.MIDI_EVENT, 0x10, 0x80, None, None, b'\x30\x00'
        )
        events = [
            meta_event, event_1_start, event_1_stop,
            event_2_start, meta_event, event_1_start,
            event_2_stop, event_1_stop
        ]
        ticks_per_quarter_note = 960
        ticks_per_note_time_unit = 1
        expected_notes = [
            notes_handling.Note(notes_handling.GUITAR_NOTE, 0x20, 0x30, 0x30),
            notes_handling.Note(notes_handling.GUITAR_NOTE, 0x30, 0x40, 0x30),
            notes_handling.Note(notes_handling.GUITAR_NOTE, 0x20, 0x30, 0x40),
        ]

        # Act
        _, notes = track_conversion.convert_events_to_notes(
            events, ticks_per_quarter_note, ticks_per_note_time_unit
        )

        # Assert
        self.assertEqual(notes, expected_notes)

    def test_convert_events_to_notes_with_rescaling_and_drum_notes(self):

        # Arrange
        meta_event = events_handling.Event(
            events_handling.META_EVENT, 0x20, 0xFF, 0x2F, 0x00, b''
        )
        event_1_start = events_handling.Event(
            events_handling.MIDI_EVENT, 0x10, 0x99, None, None, b'\x20\x40'
        )
        event_1_stop = events_handling.Event(
            events_handling.MIDI_EVENT, 0x30, 0x89, None, None, b'\x20\x00'
        )
        event_2_start = events_handling.Event(
            events_handling.MIDI_EVENT, 0x10, 0x99, None, None, b'\x30\x40'
        )
        event_2_stop = events_handling.Event(
            events_handling.MIDI_EVENT, 0x10, 0x89, None, None, b'\x30\x00'
        )
        events = [
            meta_event, event_1_start, event_1_stop,
            event_2_start, meta_event, event_1_start,
            event_2_stop, event_1_stop
        ]
        ticks_per_quarter_note = 960
        ticks_per_note_time_unit = 2
        expected_notes = [
            notes_handling.Note(notes_handling.DRUMS_NOTE, 0x20, 0x18, 0x18),
            notes_handling.Note(notes_handling.DRUMS_NOTE, 0x30, 0x20, 0x18),
            notes_handling.Note(notes_handling.DRUMS_NOTE, 0x20, 0x18, 0x20),
        ]

        # Act
        _, notes = track_conversion.convert_events_to_notes(
            events, ticks_per_quarter_note, ticks_per_note_time_unit
        )

        # Assert
        self.assertEqual(notes, expected_notes)

    def test_create_note_tokens(self):

        # Arrange
        note = notes_handling.Note(notes_handling.DRUMS_NOTE, -1, 0x00, 0x18)
        time = 0x40
        expected_start = [0x40, 1, -1]
        expected_stop = [0x58, 0, -1]

        # Act
        start, stop = track_conversion.create_note_tokens(time, note)

        # Assert
        self.assertEqual(start, expected_start)
        self.assertEqual(stop, expected_stop)

    def test_convert_token_to_event_start(self):

        # Arrange
        previous_token_time = 0
        start = [0x40, 1, 32]
        channel = 0
        ticks_per_note_time_unit = 2
        expected_event = events_handling.Event(
            events_handling.MIDI_EVENT, 0x80, 0x90, None, None, b'\x20\x40'
        )

        # Act
        event = track_conversion.convert_token_to_event(
            previous_token_time, start, channel, ticks_per_note_time_unit
        )

        # Assert
        self.assertEqual(event, expected_event)

    def test_convert_token_to_event_stop(self):

        # Arrange
        previous_token_time = 0
        start = [0x40, 0, 32]
        channel = 0
        ticks_per_note_time_unit = 2
        expected_event = events_handling.Event(
            events_handling.MIDI_EVENT, 0x80, 0x80, None, None, b'\x20\x00'
        )

        # Act
        event = track_conversion.convert_token_to_event(
            previous_token_time, start, channel, ticks_per_note_time_unit
        )

        # Assert
        self.assertEqual(event, expected_event)

    def test_convert_notes_to_events(self):

        # Arrange
        ticks_per_note_time_unit = 2
        notes = [
            notes_handling.Note(notes_handling.DRUMS_NOTE, -1, 0x00, 0x18),
            notes_handling.Note(notes_handling.DRUMS_NOTE, 0x20, 0x18, 0x18),
            notes_handling.Note(notes_handling.DRUMS_NOTE, -1, 0x18, 0x08),
            notes_handling.Note(notes_handling.DRUMS_NOTE, 0x30, 0x08, 0x18),
            notes_handling.Note(notes_handling.DRUMS_NOTE, 0x20, 0x18, 0x20),
        ]
        expected_events = [
            events_handling.Event(
                events_handling.MIDI_EVENT, 0x30, 0x99, None, None, b'\x20\x40'
            ),
            events_handling.Event(
                events_handling.MIDI_EVENT, 0x30, 0x89, None, None, b'\x20\x00'
            ),
            events_handling.Event(
                events_handling.MIDI_EVENT, 0x10, 0x99, None, None, b'\x30\x40'
            ),
            events_handling.Event(
                events_handling.MIDI_EVENT, 0x30, 0x89, None, None, b'\x30\x00'
            ),
            events_handling.Event(
                events_handling.MIDI_EVENT, 0x00, 0x99, None, None, b'\x20\x40'
            ),
            events_handling.Event(
                events_handling.MIDI_EVENT, 0x40, 0x89, None, None, b'\x20\x00'
            )
        ]

        # Act
        events = track_conversion.convert_notes_to_events(
            notes_handling.DRUMS_NOTE, notes, ticks_per_note_time_unit
        )

        # Assert
        self.assertEqual(events, expected_events)


if __name__ == '__main__':
    unittest.main()
