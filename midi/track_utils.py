"""
This module contains various track related operations for example: conversion
between note list and midi track, creation of the new track etc.
"""

from mido import Message, MetaMessage


# Numeric boundaries for integers denoting available guitar programs.
FIRST_GUITAR_PROGRAM = 24
LAST_GUITAR_PROGRAM = 31


def is_note_msg(msg):
    """
    Test, if midi message is a note message (note on/off).

    :param msg: checked midi message
    :type msg: mido Message object
    :return: boolean result of the test
    """
    return msg.type == "note_on" or msg.type == "note_off"


def is_guitar_track(track):
    """
    Check, if track is a guitar track.

    :param track: tested midi track
    :type track: list of mido package's Message objects
    :return: boolean result of the check
    """

    for msg in track:
        if (
            msg.type == "program_change"
            and not FIRST_GUITAR_PROGRAM <= msg.program <= LAST_GUITAR_PROGRAM
        ):
            return False
    return True


def is_meta_track(track):
    """
    Test, if a track contains only meta events.

    :param track: tested midi track
    :type track: list of mido Message objects
    :return: result of the test
    """
    for msg in track:
        if not msg.is_meta:
            return False
    return True


def new_guitar_track(tempo, guitar_program_i):
    """
    Create empty guitar midi track.

    :param tempo: microseconds per midi beat
    :type tempo: float or int
    :param guitar_program_i: index of the instrument program, which will be
                             assigned to this track
    :type guitar_program_i: integer in range 0 ... 7
    :return:
    """
    track = []
    tempo_change = MetaMessage(type="set_tempo", tempo=tempo)
    program_change = Message(
        type="program_change", program=FIRST_GUITAR_PROGRAM + guitar_program_i
    )
    track.append(tempo_change)
    track.append(program_change)
    return track
