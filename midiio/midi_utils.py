""" This module contains additional midi utilities. """


from mido import Message, MetaMessage


# Numeric boundaries for integers denoting available guitar programs.
FIRST_GUITAR_PROGRAM = 24
LAST_GUITAR_PROGRAM = 31


def is_note_msg(msg):
    """ Check if input message is midi note message. """
    return msg.type == "note_on" or msg.type == "note_off"


def is_guitar_track(track):
    """ Check if input track is a guitar track. """
    for msg in track:
        if (msg.type == "program_change"
                and not (FIRST_GUITAR_PROGRAM
                         <= msg.program
                         <= LAST_GUITAR_PROGRAM)):
            return False
    return True


def is_meta_track(track):
    """ Check if input track has only meta midi events. """
    for msg in track:
        if not msg.is_meta:
            return False
    return True


def create_guitar_track(tempo, guitar_program_i):
    """ Create a new empty guitar midi track. """
    tempo_change = MetaMessage(type="set_tempo", tempo=tempo)
    program_change = Message(type="program_change",
                             program=FIRST_GUITAR_PROGRAM + guitar_program_i)
    track = [tempo_change, program_change]
    return track
