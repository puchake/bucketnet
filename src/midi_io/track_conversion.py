import midi_io.events_handling as events_handling
import midi_io.notes_handling as notes_handling

import heapq

# Max interval length in quarter notes.
MAX_QUARTER_NOTES_INTERVAL = 4

# Size of events history array. There are 128 different available pitch values
# in midi file, so we don't need events history bigger than 128.
EVENTS_HISTORY_SIZE = 128

# Constants used in note start/stop token creation.
# IT IS IMPORTANT THAT STOP_TOKEN IS LOWER THAN START_TOKEN.
# There are often (if notes were earlier converter it is always) cases where
# start and stop events occur at the same time. If start token was lower than
# stop token it would lead to it being placed higher in the priority queue
# (heapq). Because of it the same note played twice in a row would have its
# second instance cut to 0 duration, because stop event for previous note
# would occur immediately after start.
START_TOKEN = 1
STOP_TOKEN = 0

# Default midi channel for created guitar events.
DEFAULT_CHANNEL = 0

# Default velocities for created note on and off events.
DEFAULT_ON_VELOCITY = 64
DEFAULT_OFF_VELOCITY = 0

# Notes values indices.
TYPE = 0
PITCH = 1
DELTA_TIME = 2
DURATION = 3

# Constant value representing triplet 1/64 note in relation to quarter note.
MINIMAL_NOTE_MULTIPLIER = 24


def get_event_note_type(event):
    """
    Get type of note corresponding to provided note event.
    :param event: provided note event
    :return: note type which matches given event
    """

    if events_handling.is_drums_event(event):
        return notes_handling.DRUMS_NOTE
    else:
        return notes_handling.GUITAR_NOTE


def convert_events_to_notes(
        events, ticks_per_quarter_note, ticks_per_note_time_unit
):
    """
    Convert list of events to notes.
    :param events: list of converted events
    :param ticks_per_quarter_note: number of midi ticks per quarter note
    :param ticks_per_note_time_unit: number of midi ticks contained in
                                     one note time unit
    :return: notes_type and list of notes
    """

    notes_values = []
    notes = []
    max_time_interval = ticks_per_quarter_note * MAX_QUARTER_NOTES_INTERVAL
    events_pairs = pair_up_events(events)
    for events_pair in events_pairs:
        start_time, delta_time, events_pitch, end_time = events_pair
        delta_time, pauses = trim_delta_time(delta_time, max_time_interval)
        duration = end_time - start_time
        note_values = [None, events_pitch, delta_time, duration]
        notes_values += pauses
        notes_values.append(note_values)

    # Trim notes durations and insert pauses into remaining empty spaces.
    fix_chords(notes_values, ticks_per_quarter_note)
    trim_chords_durations(notes_values)

    # Inserting pauses can interfere with shape of track. Trimming delta time
    # can do it too, but it occurs less often and can be useful, so it will
    # stay for now.
    #fill_empty_spaces_between_notes(notes_values)

    # Check whether events present in events list are drums events and set type
    # of all created notes accordingly. Also rescale notes durations and
    # delta times.
    notes_type = notes_handling.GUITAR_NOTE
    for event in events:
        if events_handling.is_note_event(event):
            notes_type = get_event_note_type(event)
            break
    for note_values in notes_values:
        note_values[TYPE] = notes_type
        note_values[DELTA_TIME] /= ticks_per_note_time_unit
        note_values[DURATION] /= ticks_per_note_time_unit
        notes.append(notes_handling.Note(*note_values))

    return notes_type, notes


def pair_up_events(events):
    """
    Create on and off events pairs from events list.
    :param events: list of events which will be paired
    :return: list of paired up events
    """

    events_pairs = []

    # Array used to store indices of events pairs opened by note on events.
    # Those indices will later be used to close opened events pair with note
    # off events time. Note event's pitch is used as index to this array.
    events_history = [-1] * EVENTS_HISTORY_SIZE

    time = 0
    previous_note_event_time = 0
    pairs_counter = 0
    for event in events:
        time += event.delta_time
        if not events_handling.is_note_event(event):
            continue
        events_pitch = event.data[events_handling.NOTE_DATA_PITCH]
        if events_handling.is_note_on(event):
            delta_time = time - previous_note_event_time

            # Open new events pair and append it to list.
            events_pairs.append([time, delta_time, events_pitch])
            events_history[events_pitch] = pairs_counter
            previous_note_event_time = time
            pairs_counter += 1

        # If event is note event and it is not note on event then it must be
        # note off event.
        else:

            # Close existing events pair for note off event's pitch.
            events_pairs[events_history[events_pitch]] += [time]

    return events_pairs


def trim_delta_time(delta_time, max_time_interval):
    """
    Convert delta time to max possible time interval if it exceeds
    it and convert remaining time to pauses.
    :param delta_time: trimmed delta time value
    :param max_time_interval: time interval limit, boundary for delta time
    :return: converted interval, list of pauses
    """

    # Return unmodified delta time and empty list of pauses if the interval
    # doesn't exceed set bounds.
    if delta_time <= max_time_interval:
        return delta_time, []

    pauses = []

    # Create last pause which will be used to trim delta time.
    last_pause = [
        None, notes_handling.PAUSE_PITCH,
        max_time_interval, delta_time % max_time_interval
    ]

    # Create full pauses list.
    number_of_full_pauses = delta_time // max_time_interval - 1
    pauses += [
        [
            None, notes_handling.PAUSE_PITCH,
            max_time_interval, max_time_interval
        ] for i in range(number_of_full_pauses)
    ]

    # Append last pause to pauses list if it is necessary.
    if last_pause[DURATION] != 0:
        pauses.append(last_pause)
        delta_time = last_pause[DURATION]
    else:
        delta_time = max_time_interval

    return delta_time, pauses


def fix_chords(notes_values, ticks_per_quarter_note):
    """
    Fix chord notes to begin at the same time and end at the same time.
    :param notes_values: notes to fix
    :param ticks_per_quarter_note: value used to determine minimal
                                   ticks per note
    :return: -
    """

    minimal_interval = ticks_per_quarter_note // MINIMAL_NOTE_MULTIPLIER
    for i in range(len(notes_values)):
        if notes_values[i][DELTA_TIME] < minimal_interval:
            notes_values[i][DURATION] += notes_values[i][DELTA_TIME]
            if i + 1 < len(notes_values):
                notes_values[i + 1][DELTA_TIME] += notes_values[i][DELTA_TIME]
            notes_values[i][DELTA_TIME] = 0


def trim_chords_durations(notes_values):
    """
    Trim chords notes to equal durations. Modifies list in place.
    :param notes_values: array of notes values
    :return: -
    """

    chord = []
    durations_in_chord = []

    for i in range(len(notes_values)):

        # If note is chord note (delta time = 0) append it to current chord.
        # Otherwise trim durations of all chord notes to shorter of
        # shortest note in chord or current note's delta time.
        if notes_values[i][DELTA_TIME] == 0:
            chord.append(i)
            durations_in_chord.append(notes_values[i][DURATION])
        else:
            if chord:
                notes_duration = min(
                    *durations_in_chord, notes_values[i][DELTA_TIME]
                )
                for j in chord:
                    notes_values[j][DURATION] = notes_duration
            chord = [i]
            durations_in_chord = [notes_values[i][DURATION]]

    return


def fill_empty_spaces_between_notes(notes_values):
    """
    Insert pauses into empty spaces between notes. Modify notes list in place.
    Every pause inserted by this function wont be longer than max allowed time
    interval, because functions previously used in events -> notes conversion
    (delta time trimming) filled all empty spaces longer than max allowed time
    interval with full pauses.
    :param notes_values: notes values
    :return: -
    """

    pauses = []
    previous_duration = 0
    for i in range(len(notes_values)):

        # If there is space between notes save this index to insert a pause
        # there later. Also change currents note delta time to match future
        # pause start point.
        if notes_values[i][DELTA_TIME] > previous_duration:
            duration = notes_values[i][DELTA_TIME] - previous_duration
            pauses.append([i, previous_duration, duration])
            notes_values[i][DELTA_TIME] = duration

        previous_duration = notes_values[i][DURATION]

    # With each inserted pause insertion indices of next pauses need to be
    # incremented. This counter takes care of that.
    pauses_counter = 0

    # Insert all pauses in their places.
    for insertion_index, delta_time, duration in pauses:
        pause = [None, notes_handling.PAUSE_PITCH, delta_time, duration]
        notes_values.insert(insertion_index + pauses_counter, pause)
        pauses_counter += 1


def convert_notes_to_events(notes_type, notes, ticks_per_note_time_unit):
    """
    Convert track's notes to events.
    :param notes_type: type of notes contained in notes list
    :param notes: list of notes which are being converted
    :param ticks_per_note_time_unit: number of midi ticks contained in
                                     one note time unit
    :return: list of events
    """

    events = []
    notes_tokens = []
    time = 0

    # Push start and stop tokens of every note on heap.
    for note in notes:
        time += note.delta_time
        if note.pitch != notes_handling.PAUSE_PITCH:
            start, stop = create_note_tokens(time, note)
            heapq.heappush(notes_tokens, start)
            heapq.heappush(notes_tokens, stop)

    # Determine midi output channel.
    if notes_type == notes_handling.GUITAR_NOTE:
        channel = DEFAULT_CHANNEL
    else:
        channel = events_handling.DRUMS_CHANNEL

    time = 0

    # Get tokens in order from the earliest to the latest and
    # append events created from them to events list.
    while notes_tokens:
        token = heapq.heappop(notes_tokens)
        event = convert_token_to_event(
            time, token, channel, ticks_per_note_time_unit
        )
        events.append(event)
        time = token[0]

    return events


def create_note_tokens(time, note):
    """
    Convert note to pair of start/stop tokens.
    :param time: note start time in note time units
    :param note: note to convert
    :return: pair of tokens which indicate note's start and stop.
    """

    start = [time, START_TOKEN, note.pitch]
    stop = [time + note.duration, STOP_TOKEN, note.pitch]
    return start, stop


def convert_token_to_event(
        previous_token_time, token, channel, ticks_per_note_time_unit
):
    """
    Get event representing given token.
    :param previous_token_time: time of previous token
    :param token: token to convert
    :param channel: channel to which event should belong
    :param ticks_per_note_time_unit: number of midi ticks contained in
                                     one note time unit
    :return: created event
    """

    token_time, token_type, pitch  = token

    # Important conversion of float values to int which allows vlq write.
    delta_time = int(
        ticks_per_note_time_unit * (token_time - previous_token_time)
    )

    # Set other event's parameters basing on token.
    if token_type == START_TOKEN:
        status_code = events_handling.NOTE_ON | channel
        data = bytes([pitch, DEFAULT_ON_VELOCITY])
    else:
        status_code = events_handling.NOTE_OFF | channel
        data = bytes([pitch, DEFAULT_OFF_VELOCITY])

    # Create midi event with set parameters and return it.
    event = events_handling.Event(
        events_handling.MIDI_EVENT, delta_time, status_code, None, None, data
    )
    return event
