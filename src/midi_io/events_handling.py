from collections import namedtuple


# Initialize named tuple which represents event.
Event = namedtuple(
    "Event",
    ["type", "delta_time", "status_code", "meta_type", "length", "data"]
)

# Constants for events types.
MIDI_EVENT = 0
META_EVENT = 1
SYSEX_EVENT = 2

# Status codes identifying event types.
MIDI_EVENT_CODES = [0x80, 0x90, 0xA0, 0xB0, 0xC0, 0xD0, 0xE0]
META_EVENT_CODES = [0xFF]
SYSEX_EVENT_CODES = [0xF0, 0xF7]

# Dictionary of midi event's lengths with types as keys.
MIDI_EVENT_LENGTHS = {
    0x80: 2, 0x90: 2, 0xA0: 2, 0xB0: 2, 0xC0: 1, 0xD0: 1, 0xE0: 2
}

# End of track meta event's meta type.
END_OF_TRACK_META_TYPE = 0x2F

# Note on and note off midi event's types.
NOTE_ON = 0x90
NOTE_OFF = 0x80

# Note event's data indices for pitch and velocity.
NOTE_DATA_PITCH = 0
NOTE_DATA_VELOCITY = 1

# Constant midi channel for percussion events.
DRUMS_CHANNEL = 0x09

# Masks for midi event type and channel extraction.
MIDI_EVENT_TYPE_MASK = 0b11110000
MIDI_EVENT_CHANNEL_MASK = 0b00001111

# VLQ reading constants.
VLQ_CONTINUATION_BIT = 0b10000000
VLQ_BYTE_VALUE_BITS = 0b01111111
VALUE_BITS_PER_VLQ_BYTE = 7


def read_vlq(source):
    """
    Read next variable length quantity from source's bytes.
    :param source: object which contains bytes for reading.
    :return: read vlq value
    """

    # Read first byte from source and save its value.
    byte = source.read(1)[0]
    value = byte & VLQ_BYTE_VALUE_BITS

    # Keep appending values from read vlq bytes while previously read byte has
    # its continuation bit set to 1.
    while byte & VLQ_CONTINUATION_BIT != 0:
        value <<= VALUE_BITS_PER_VLQ_BYTE
        byte = source.read(1)[0]
        value += byte & VLQ_BYTE_VALUE_BITS

    return value


def write_vlq(destination, value):
    """
    Write value to byte buffer in variable length quantity format.
    :param destination: object to which value will be written
    :param value: saved value
    :return: -
    """

    # Write first value's byte and delete used bits with shift.
    vlq_bytes = bytes([value & VLQ_BYTE_VALUE_BITS])
    value >>= VALUE_BITS_PER_VLQ_BYTE

    # Keep writing bytes while there are some non zero bits left in value.
    while value > 0:
        vlq_bytes += bytes(
            [VLQ_CONTINUATION_BIT | (value & VLQ_BYTE_VALUE_BITS)]
         )
        value >>= VALUE_BITS_PER_VLQ_BYTE

    destination.write(vlq_bytes[::-1])


def read_event(source):
    """
    Read next event from bytes of source.
    :param source: object which represents reading source
    :return: event parsed from read bytes
    """

    delta_time = read_vlq(source)
    status_code = source.read(1)[0]

    if (status_code & MIDI_EVENT_TYPE_MASK) in MIDI_EVENT_CODES:

        # If currently read event is midi event read its data.
        event_type = MIDI_EVENT
        meta_type = None
        length = None
        midi_type = status_code & MIDI_EVENT_TYPE_MASK
        data = source.read(MIDI_EVENT_LENGTHS[midi_type])

    elif status_code in META_EVENT_CODES:

        # Read remaining meta event's data.
        event_type = META_EVENT
        meta_type = source.read(1)[0]
        length = read_vlq(source)
        data = source.read(length)

    elif status_code in SYSEX_EVENT_CODES:

        # Read remaining system exclusive event's data.
        event_type = SYSEX_EVENT
        meta_type = None
        length = read_vlq(source)
        data = source.read(length)

    else:

        # TODO exception?
        print("Error: unrecognizable status code")
        return None

    return Event(event_type, delta_time, status_code, meta_type, length, data)


def write_event(destination, event):
    """
    Output event as bytes to destination.
    :param destination: object, destination for writing
    :param event: event outputted to destination
    :return: -
    """

    write_vlq(destination, event.delta_time)
    destination.write(bytes([event.status_code]))

    # Based on event's type output necessary event's parameters to destination.
    if event.type == MIDI_EVENT:
        destination.write(event.data)
    elif event.type == META_EVENT:
        destination.write(bytes([event.meta_type]))
        write_vlq(destination, event.length)
        destination.write(event.data)
    elif event.type == SYSEX_EVENT:
        write_vlq(destination, event.length)
        destination.write(event.data)


def is_end_of_track(event):
    """
    Check if event is end of track event.
    :param event: checked event
    :return: check result
    """

    return event.type == META_EVENT and \
           event.meta_type == END_OF_TRACK_META_TYPE


def is_note_event(event):
    """
    Check whether event is note event or not.
    :param event: checked event
    :return: result
    """

    midi_type = event.status_code & MIDI_EVENT_TYPE_MASK
    return midi_type == NOTE_ON or midi_type == NOTE_OFF


def is_note_on(event):
    """
    Check if note is midi note on event.
    :param event: event to check
    :return: check result
    """

    return (event.status_code & MIDI_EVENT_TYPE_MASK) == NOTE_ON and \
           event.data[NOTE_DATA_VELOCITY] != 0


def is_note_off(event):
    """
    Check if given event is note off event.
    :param event: checked event
    :return: check result
    """

    return (event.status_code & MIDI_EVENT_TYPE_MASK) == NOTE_OFF or \
           ((event.status_code & MIDI_EVENT_TYPE_MASK) == NOTE_ON and
            event.data[NOTE_DATA_VELOCITY] == 0)


def is_drums_event(event):
    """
    Check if event is related to midi percussion channel.
    :param event: checked event
    :return: check result
    """

    return (event.status_code & MIDI_EVENT_CHANNEL_MASK) == DRUMS_CHANNEL


def is_events_list_empty(events):
    """
    Check if list of events contains any note related events.
    :param events: list of events to check
    :return: check result
    """

    for event in events:
        if is_note_event(event):
            return False

    return True
