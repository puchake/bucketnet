from ..events.MidiEvent import MidiEvent
from ..events.MetaEvent import MetaEvent
from ..events.SysexEvent import SysexEvent
from ..events.EventTypes import EventTypes
from ..events.MidiEventTypes import MidiEventTypes


class EventUtilities:

    MIN_MIDI_STATUS_CODE = 0x80
    MAX_MIDI_STATUS_CODE = 0xEF
    META_STATUS_CODE = 0xFF
    SYSEX_STATUS_CODE = 0xF0
    SYSEX_ESCAPE_CODE = 0xF7

    MIDI_EVENT_LENGTHS = \
        {
            MidiEventTypes.NOTE_OFF: 2, MidiEventTypes.NOTE_ON: 2,
            MidiEventTypes.POLYPHONIC_PRESSURE: 2,
            MidiEventTypes.CONTROLLER: 2,
            MidiEventTypes.PROGRAM_CHANGE: 1,
            MidiEventTypes.CHANNEL_PRESSURE: 1,
            MidiEventTypes.PITCH_BEND: 2
        }

    VALUE_BITS_PER_VLQ_BYTE = 7
    MAX_VALUE_IN_VQL_BYTE = 127
    VLQ_CONTINUATION_BIT = 0b10000000

    @staticmethod
    def read_event(source_bytes):

        delta_time = EventUtilities._read_vlq(source_bytes)
        status_code = source_bytes.read(1)[0]

        if EventUtilities.MAX_MIDI_STATUS_CODE >= \
                status_code >= \
                EventUtilities.MIN_MIDI_STATUS_CODE:

            return EventUtilities._read_midi_event(
                source_bytes, delta_time, status_code
            )

        elif status_code == EventUtilities.META_STATUS_CODE:

            return EventUtilities._read_meta_event(
                source_bytes, delta_time, status_code
            )

        else:

            return EventUtilities._read_sysex_event(
                source_bytes, delta_time, status_code
            )

    @staticmethod
    def convert_event_to_bytes(event):
        if event.type == EventTypes.MIDI_EVENT:

            return EventUtilities._convert_midi_event_to_bytes(event)

        elif event.type == EventTypes.META_EVENT:

            return EventUtilities._convert_meta_event_to_bytes(event)

        else:

            return  EventUtilities._convert_sysex_event_to_bytes(event)

    @staticmethod
    def _read_vlq(source_bytes):

        byte = source_bytes.read(1)[0]
        value = byte & EventUtilities.MAX_VALUE_IN_VQL_BYTE

        while byte & EventUtilities.VLQ_CONTINUATION_BIT != 0:
            value <<= EventUtilities.VALUE_BITS_PER_VLQ_BYTE
            byte = source_bytes.read(1)[0]
            value += byte & EventUtilities.MAX_VALUE_IN_VQL_BYTE

        return value

    @staticmethod
    def _convert_vlq_to_bytes(value):

        vlq_bytes = bytes([value & EventUtilities.MAX_VALUE_IN_VQL_BYTE])
        value >>= EventUtilities.VALUE_BITS_PER_VLQ_BYTE

        while value > 0:
            vlq_bytes += bytes(
                [
                    EventUtilities.VLQ_CONTINUATION_BIT |
                    (value & EventUtilities.MAX_VALUE_IN_VQL_BYTE)
                ]
            )
            value >>= EventUtilities.VALUE_BITS_PER_VLQ_BYTE

        return vlq_bytes[::-1]

    @staticmethod
    def _read_midi_event(source_bytes, delta_time, status_code):

        data_length = \
            EventUtilities.MIDI_EVENT_LENGTHS[
                status_code & MidiEvent.MIDI_TYPE_MASK
            ]
        data = source_bytes.read(data_length)

        return MidiEvent(delta_time, status_code, data)

    @staticmethod
    def _read_meta_event(source_bytes, delta_time, status_code):

        meta_type = source_bytes.read(1)[0]
        data_length = EventUtilities._read_vlq(source_bytes)
        data = source_bytes.read(data_length)

        return MetaEvent(
            delta_time, status_code, meta_type, data_length, data
        )

    @staticmethod
    def _read_sysex_event(source_bytes, delta_time, status_code):

        data_length = EventUtilities._read_vlq(source_bytes)
        data = source_bytes.read(data_length)

        return SysexEvent (delta_time, status_code, data_length, data)

    @staticmethod
    def _convert_midi_event_to_bytes(event):
        return EventUtilities._convert_vlq_to_bytes(event.delta_time) + \
               bytes([event.status_code]) + \
               event.data

    @staticmethod
    def _convert_meta_event_to_bytes(event):
        return EventUtilities._convert_vlq_to_bytes(event.delta_time) + \
               bytes([event.status_code, event.meta_type]) + \
               EventUtilities._convert_vlq_to_bytes(event.length) + \
               event.data

    @staticmethod
    def _convert_sysex_event_to_bytes(event):
        return EventUtilities._convert_vlq_to_bytes(event.delta_time) + \
               bytes([event.status_code]) + \
               EventUtilities._convert_vlq_to_bytes(event.length) + \
               event.data
