""" This module contains class capable of infering. """


import pickle
import tensorflow as tf
import numpy as np

from processing.data_utils import encode_tune_text, decode_tune_matrix


class Composer:
    """
    This class describes object capable of music composition with learned lstm
    model.
    """

    IN_TEMPERATURE = "temperature"
    IN_GENERATION_DATA = "in_generation_data"
    IN_GENERATION_STATE = "in_generation_state"
    IN_LSTM_DROPOUT = "in_lstm_dropout"
    GENERATED_SYMBOLS = "generated_symbols"
    GENERATED_STATE = "generated_state"

    def __init__(self, model_file_path, meta_file_path, encoder_file_path,
                 decoder_file_path):
        """ Setup environment. """
        self._session = tf.Session()
        saver = tf.train.import_meta_graph(meta_file_path)
        saver.restore(self._session, model_file_path)
        self._in_temperature = tf.get_collection(self.IN_TEMPERATURE)[0]
        self._in_generation_data = tf.get_collection(self.IN_GENERATION_DATA)[0]
        self._in_generation_state = tf.get_collection(
            self.IN_GENERATION_STATE
        )[0]
        self._in_lstm_dropout = tf.get_collection(self.IN_LSTM_DROPOUT)[0]
        self._generated_symbols = tf.get_collection(self.GENERATED_SYMBOLS)[0]
        self._get_generated_state()
        self._load_encoding(encoder_file_path, decoder_file_path)

    def compose(self, tune_text, generation_length):
        """
        Generate generation_length new symbols and append them to tune_text.
        """
        state = np.zeros([len(self._generated_state), 2, 1,
                          self._generated_state[0].c.shape.as_list()[-1]])
        generated_text = ""
        for i in range(len(tune_text) + generation_length):
            if i < len(tune_text):
                encoded_char = encode_tune_text(tune_text[i], self._encoder)
            else:
                encoded_char = generated_char
            generated_char, state = self._session.run(
                [self._generated_symbols, self._generated_state],
                feed_dict={self._in_temperature: 0.5,
                           self._in_generation_data: encoded_char,
                           self._in_generation_state: state,
                           self._in_lstm_dropout: 0.0}
            )
            state = np.array(state)
            if i >= len(tune_text):
                generated_text += decode_tune_matrix(generated_char,
                                                     self._decoder)
        return tune_text + generated_text

    def close(self):
        self._session.close()

    def _get_generated_state(self):
        """ LSTM state collection needs to be read in a special way. """
        states = []
        state_collection = tf.get_collection(self.GENERATED_STATE)
        for i in range(0, len(state_collection), 2):
            states.append(
                tf.nn.rnn_cell.LSTMStateTuple(state_collection[i],
                                              state_collection[i + 1])
            )
        self._generated_state = tuple(states)

    def _load_encoding(self, encoder_file_path, decoder_file_path):
        """ Load encoder and decoder from provided file paths. """
        with open(encoder_file_path, "rb") as file:
            self._encoder = pickle.load(file)
        with open(decoder_file_path, "rb") as file:
            self._decoder = pickle.load(file)
