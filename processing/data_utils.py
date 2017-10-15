"""
This module contains functions which deal with data loading and filtering.
"""


import csv

import numpy as np


__all__ = ["COLUMNS_COUNT", "TUNE", "SETTING", "NAME", "TYPE", "METER", "MODE",
           "ABC", "DATE", "USERNAME", "extract_columns", "is_matching",
           "read_csv", "find_charset", "create_encoding", "encode_tune_text",
           "decode_tune_matrix"]


COLUMNS_COUNT = 9
# Constant indices of csv row elements.
(TUNE, SETTING, NAME, TYPE,
 METER, MODE, ABC, DATE, USERNAME) = range(COLUMNS_COUNT)


def extract_columns(row, columns_to_extract):
    """ Extract selected columns from the given row. """
    new_row = []
    for column in columns_to_extract:
        new_row.append(row[column])
    return new_row


def is_matching(row, tune_types=None):
    """ Check, if the given tune row matches filtering parameters. """
    matches = True
    if tune_types is not None:
        type_matches = False
        for tune_type in tune_types:
            type_matches = type_matches or row[TYPE] == tune_type
        matches = matches and type_matches
    return matches


def read_csv(file_path, columns_to_extract, filtering_params):
    """ Read tunes from given csv path. """
    with open(file_path, "r", encoding="utf-8") as file:
        # Quotes inside abc text are escaped with \ character.
        csv_reader = csv.reader(file, escapechar="\\", doublequote=False)
        read_rows = []
        # Skip the header row.
        next(csv_reader)
        for row in csv_reader:
            if is_matching(row, **filtering_params):
                read_rows.append(extract_columns(row, columns_to_extract))
    return read_rows


def find_charset(texts):
    """ Find set of unique characters from given list of texts. """
    charset = set()
    for text in texts:
        charset = charset.union(set(text))
    return charset


def create_encoding(charset):
    """ Create encode and decode dictionaries. """
    encoder = {char: i for i, char in enumerate(charset)}
    decoder = {i: char for i, char in enumerate(charset)}
    return encoder, decoder


def encode_tune_text(tune_text, encoder):
    """ Encode given tune text to one-hot format with provided encoder. """
    tune_matrix = np.zeros([len(tune_text), len(encoder)])
    for i, char in enumerate(tune_text):
        tune_matrix[i, encoder[char]] = 1.0
    return tune_matrix


def decode_tune_matrix(tune_matrix, decoder):
    """ Decode given 2D one-hot tune representation to string format. """
    chars_indices = np.argmax(tune_matrix, axis=1)
    tune_text = ""
    for char_index in chars_indices:
        tune_text += decoder[char_index]
    return tune_text
