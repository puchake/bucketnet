"""
This module contains definition of a class which manages training examples for
models.
"""


import pickle
from os import path
from random import shuffle

import numpy as np

from processing.data_utils import *


class Dataset:
    """ This class defines dataset which provides training examples  """

    SUBSETS_COUNT = 3
    # Constant indices of subsets of tunes in _tunes list.
    TRAIN, VAL, TEST = range(SUBSETS_COUNT)

    def __init__(self, file_path, filtering_params, batch_size, roll_out,
                 subsets_sizes):
        self._batch_size = batch_size
        self._roll_out = roll_out
        self._init_sets(file_path, filtering_params, subsets_sizes, roll_out)
        self._init_encoding()
        self._init_queues()
        self._init_batching()

    def get_next_batch(self, set_index, lstm_state):
        """ Get next batch of tunes text from selected set. """
        queue_reset_occurred = False
        while self._check_current_tunes(set_index, lstm_state):
            fill_reset = self._fill_empty_indices(set_index)
            queue_reset_occurred = queue_reset_occurred or fill_reset
        self._fill_batch_matrix(set_index)
        self._advance_batch(set_index)
        return self._batch_matrix, queue_reset_occurred

    def get_charset_size(self):
        """ Access point for the charset size of the dataset. """
        return self._charset_size

    def save_encoding(self, dir_path):
        """ Save encoder and decoder in target directory. """
        with open(path.join(dir_path, "encoder.dict"), "wb") as file:
            pickle.dump(self._encoder, file)
        with open(path.join(dir_path, "decoder.dict"), "wb") as file:
            pickle.dump(self._decoder, file)

    def _fill_batch_matrix(self, set_index):
        """ Fill in the batch matrix. """
        for i in range(self._batch_size):
            tune_index = self._tunes_indices[set_index][i]
            tune_position = self._tunes_positions[set_index][i]
            tune_fragment = (self._tunes[set_index][tune_index]
                             [tune_position:tune_position + self._roll_out])
            self._batch_matrix[:, i, :] = encode_tune_text(tune_fragment,
                                                           self._encoder)

    def _advance_batch(self, set_index):
        """ Advance tunes position by the length of LSTM roll out. """
        for i in range(self._batch_size):
            self._tunes_positions[set_index][i] += self._roll_out

    def _reset_queue(self, set_index):
        """
        Reset queue of elements which will be provided consecutively to the
        model.
        """
        # We use list for efficient dynamic sizing.
        self._queues[set_index] = list(
            np.random.permutation(len(self._tunes[set_index]))
        )

    def _check_current_tunes(self, set_index, lstm_state):
        """
        Check, if tunes currently used in the batch have enough characters left
        for another training iteration with given roll_out. Discard indices
        of tunes which don't satisfy this requirement and reset state for those
        tunes.
        """
        reset_occurred = False
        for i in range(self._batch_size):
            tune_len = len(
                self._tunes[set_index][self._tunes_indices[set_index][i]]
            )
            current_tune_position = self._tunes_positions[set_index][i]
            if current_tune_position + self._roll_out > tune_len:
                reset_occurred = True
                self._tunes_indices[set_index][i] = None
                self._tunes_positions[set_index][i] = 0
                # State is in shape of [layers, 2, batch, num_neurons] and we
                # reset every element of state for selected batch index.
                for layer_state in lstm_state:
                    layer_state[:, i] = 0
        return reset_occurred

    def _fill_empty_indices(self, set_index):
        """
        Fill in empty tune indices for given set with the next indices taken
        from tunes queue. Reset queue, if there are no tunes left in it.
        """
        queue_reset_occurred = False
        for i in range(self._batch_size):
            if self._tunes_indices[set_index][i] is None:
                if len(self._queues[set_index]) == 0:
                    queue_reset_occurred = True
                    self._reset_queue(set_index)
                self._tunes_indices[set_index][i] = (self._queues[set_index]
                                                     .pop())
        return queue_reset_occurred

    # Initialization routines.

    def _init_sets(self, file_path, filtering_params, subsets_sizes, roll_out):
        """ Initialize train, validation and tests subsets. """
        train_size, val_size, _ = subsets_sizes
        tunes = read_csv(file_path, [ABC], filtering_params)
        # Extract only text from list of elements.
        for i in range(len(tunes)):
            tunes[i] = tunes[i][0]
            # Pad tunes at the end with newline characters.
            tunes[i] += "\n" * (roll_out - (len(tunes) % roll_out))
        shuffle(tunes)
        # Split tunes between train, validation and test subsets.
        first_split = int(train_size * len(tunes))
        second_split = int((val_size + train_size) * len(tunes))
        self._tunes = [None] * self.SUBSETS_COUNT
        self._tunes[self.TRAIN] = tunes[:first_split]
        self._tunes[self.VAL] = tunes[first_split:second_split]
        self._tunes[self.TEST] = tunes[second_split:]

    def _init_encoding(self):
        """ Initialize encoder and decoder used by dataset. """
        charset = find_charset(self._tunes[self.TRAIN])
        charset = charset.union(find_charset(self._tunes[self.VAL]))
        charset = charset.union(find_charset(self._tunes[self.TEST]))
        self._charset_size = len(charset)
        self._encoder, self._decoder = create_encoding(charset)

    def _init_queues(self):
        """
        Initialize queues of elements, which will be consecutively supplied in
        training.
        """
        self._queues = [None] * self.SUBSETS_COUNT
        for i in [self.TRAIN, self.VAL, self.TEST]:
            self._reset_queue(i)

    def _init_batching(self):
        """
        Create structures needed to batch train, validation and test sets. Those
        structures are list of indices of currently used tunes and list of
        text positions in those tunes.
        """
        self._tunes_indices = [None] * self.SUBSETS_COUNT
        self._tunes_positions = [None] * self.SUBSETS_COUNT
        for i in range(self.SUBSETS_COUNT):
            self._tunes_indices[i] = [None] * self._batch_size
            self._tunes_positions[i] = [0] * self._batch_size
            self._fill_empty_indices(i)
        self._batch_matrix = np.zeros(
            [self._roll_out, self._batch_size, self._charset_size]
        )
