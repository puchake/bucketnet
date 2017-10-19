""" This module provides tensorflow graph building functions. """


import tensorflow as tf


__all__ = ["build_lstm_cell", "build_linear_layer", "build_train_graph",
           "build_generation_graph"]


def build_lstm_cell(layers_count, layers_size, in_lstm_dropout):
    """ Build multi-layer lstm cell, where all layers have the same size. """
    cells = []
    for i in range(layers_count):
        cell = tf.contrib.rnn.BasicLSTMCell(layers_size)
        if i != layers_count - 1:
            cell = tf.contrib.rnn.DropoutWrapper(
                cell, output_keep_prob=1.0 - in_lstm_dropout
            )
        cells.append(cell)
    return tf.contrib.rnn.MultiRNNCell(cells)


def build_linear_layer(name, in_size, out_size):
    """ Build one fully-connected layer without activations. """
    with tf.variable_scope(name):
        weights = tf.get_variable(
            "weights", shape=[in_size, out_size], dtype=tf.float32,
            initializer=tf.contrib.layers.xavier_initializer()
        )
        biases = tf.get_variable(
            "biases", shape=[1, out_size], dtype=tf.float32,
            initializer=tf.constant_initializer()
        )
    return weights, biases


def build_train_graph(cell, out_weights, out_biases, previous_state, in_data,
                      roll_out, charset_size):
    """ Build lstm train graph with roll_out number of steps. """
    outs = []
    state = []
    # Reformat previous state to fit tensorflow requirements.
    for i in range(previous_state.shape[0]):
        state.append((previous_state[i, 0], previous_state[i, 1]))
    for i in range(roll_out):
        out, state = cell(in_data[i], state)
        outs.append(out)
    final_outs = tf.matmul(tf.concat(outs, axis=0), out_weights) + out_biases
    final_outs = tf.reshape(final_outs, [roll_out, -1, charset_size])
    return final_outs, state


def build_generation_graph(cell, out_weights, out_biases, previous_state,
                           in_data, temperature):
    """ Build one step lstm graph used in generation. """
    state = []
    # Reformat previous state to fit tensorflow requirements.
    for i in range(previous_state.shape[0]):
        state.append((previous_state[i, 0], previous_state[i, 1]))
    out, state = cell(in_data, state)
    final_out = tf.matmul(out, out_weights) + out_biases
    generated_class = tf.one_hot(tf.multinomial(final_out / temperature, 1),
                                 final_out.shape[-1])
    generated_class = tf.squeeze(generated_class, [0])
    return generated_class, state
