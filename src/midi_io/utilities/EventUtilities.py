from ..events.MidiEvent import MidiEvent
from ..events.MetaEvent import MetaEvent
from ..events.SysexEvent import SysexEvent
from ..events.MidiEventTypes import MidiEventTypes


class EventUtilities:
    """
    Utilities class for events.
    """

    # Constants used to determine event type based on read status code.
    MIN_MIDI_STATUS_CODE = 0x80
    MAX_MIDI_STATUS_CODE = 0xEF
    META_STATUS_CODE = 0xFF

    # midi-event-type -> number-of-data-bytes dictionary
    MIDI_EVENT_LENGTHS = {
                             MidiEventTypes.NOTE_OFF: 2,
                             MidiEventTypes.NOTE_ON: 2,
                             MidiEventTypes.POLYPHONIC_PRESSURE: 2,
                             MidiEventTypes.CONTROLLER: 2,
                             MidiEventTypes.PROGRAM_CHANGE: 1,
                             MidiEventTypes.CHANNEL_PRESSURE: 1,
                             MidiEventTypes.PITCH_BEND: 2
                         }

    @staticmethod
    def read_event(source):
        """
        Read bytes from source and create event object based on them.

        :param source: MidiBytesIO objects which is source for reading
        :return: new event object read from source
        """

        # Read delta time and status code byte from source.
        delta_time = source.read_vlq()
        status_code = source.read_byte()

        # Proceed with reading remaining event data and creating event object
        # based on previously read status code.
        if EventUtilities.MAX_MIDI_STATUS_CODE >= \
                status_code >= \
                EventUtilities.MIN_MIDI_STATUS_CODE:

            # Create and return new midi event.
            data = EventUtilities._read_midi_event_data(source, status_code)
            return MidiEvent(delta_time, status_code, data)

        elif status_code == EventUtilities.META_STATUS_CODE:

            # Create and return new meta event.
            meta_type, data_length, data = \
                EventUtilities._read_meta_event_data(source)
            return MetaEvent(
                       delta_time, status_code, meta_type, data_length, data
                   )

        else:

            # Create and return new sysex event.
            data_length, data = EventUtilities._read_sysex_event_data(source)
            return SysexEvent(delta_time, status_code, data_length, data)

    @staticmethod
    def _read_midi_event_data(source, status_code):
        """
        Read remaining meta event data from source.

        :param source: MidiBytesIO objects which is source for reading
        :param status_code: previously read event status code, which is
                            used to determine number of event's data bytes
        :return: data
        """

        # Access event's data length value saved in MIDI_EVENT_LENGTHS
        # dictionary by its midi type.
        data_length = EventUtilities.MIDI_EVENT_LENGTHS[
                          MidiEventTypes(
                              status_code & MidiEvent.MIDI_TYPE_MASK
                          )
                      ]

        data = source.read(data_length)
        return data

    @staticmethod
    def _read_meta_event_data(source):
        """
        Read remaining meta event data from source.

        :param source: MidiBytesIO objects which is source for reading
        :return: meta event type, data length, data
        """

        meta_type = source.read_byte()
        data_length = source.read_vlq()
        data = source.read(data_length)
        return meta_type, data_length, data

    @staticmethod
    def _read_sysex_event_data(source):
        """
        Read remaining system exclusive event data from source.

        :param source: MidiBytesIO objects which is source for reading
        :return: system exclusive event data length, data
        """

        data_length = source.read_vlq()
        data = source.read(data_length)
        return data_length, data
