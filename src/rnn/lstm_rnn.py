import tensorflow as tf
import src.midi_io.notes_handling as notes_handling
import src.rnn.rnn_loss as rnn_loss
import src.midi_io.file_io as file_io
import numpy as np


DRUMS_NOTE_LENGTH = notes_handling.DRUMS_PITCH_VECTOR_LENGTH + \
                    2 * notes_handling.TIME_VECTOR_LENGTH

NUMBER_OF_LAYERS = 3
HIDDEN_SIZE = 256
STATES_PER_LAYER = 2

TRAIN_ROLL_OUT = 200
GENERATION_ROLL_OUT = 1000


def create_cell(in_size, hidden_size):
    cell = tf.contrib.rnn.BasicLSTMCell(hidden_size)
    multi_cell = tf.contrib.rnn.MultiRNNCell([cell] * NUMBER_OF_LAYERS)
    out_weights = tf.get_variable(
        "out_weights",
        shape=[hidden_size, in_size],
        initializer=tf.contrib.layers.xavier_initializer()
    )
    out_biases = tf.get_variable(
        "out_biases",
        shape=[in_size],
        initializer=tf.constant_initializer()
    )
    return multi_cell, out_weights, out_biases


def create_train_graph(
        cell, out_weights, out_biases, roll_out,
        train_in, previous_state, learning_rate
):
    state = (
        (previous_state[0, 0], previous_state[0, 1]),
        (previous_state[1, 0], previous_state[1, 1]),
        (previous_state[2, 0], previous_state[2, 1])
    )
    out_states = []
    for i in range(roll_out):
        with tf.variable_scope("", reuse=(i != 0)):
            out_state, state = cell(train_in[i:i + 1], state)
        out_states.append(out_state)

    out = tf.matmul(tf.concat(out_states, 0), out_weights) + out_biases
    pitch_out, pitch_in, \
    delta_time_out, delta_time_in, \
    duration_out, duration_in = rnn_loss.slice_outputs(
        out[:-1], train_in[1:], notes_handling.DRUMS_NOTE
    )
    pitch_loss = rnn_loss.create_drums_pitch_loss(pitch_out, pitch_in, 1)
    delta_time_loss = rnn_loss.create_time_loss_node(
        delta_time_out, delta_time_in, 1, 1
    )
    duration_loss = rnn_loss.create_time_loss_node(
        duration_out, duration_in, 1, 1
    )
    loss = pitch_loss + delta_time_loss + duration_loss
    trainer = tf.train.AdagradOptimizer(learning_rate)
    gradients_and_variables = trainer.compute_gradients(loss)
    capped_gradients_and_variables = [
        (tf.clip_by_value(gradient, -5, 5), variable)
        for gradient, variable in gradients_and_variables
    ]
    train = trainer.apply_gradients(capped_gradients_and_variables)

    return loss, train, state


def create_generation_graph(
        cell, out_weights, out_biases, generation_in,
        generation_state, temperature
):
    generation_sstate = (
        (generation_state[0, 0], generation_state[0, 1]),
        (generation_state[1, 0], generation_state[1, 1]),
        (generation_state[2, 0], generation_state[2, 1])
    )
    with tf.variable_scope("", reuse=True):
        out, generation_sstate = cell(generation_in, generation_sstate)
    out = tf.matmul(out, out_weights) + out_biases
    print(out.shape)
    pitch = out[0:1, :27]
    delta_time_length = out[0:1, 27:35]
    delta_time_type = out[0:1, 35:38]
    duration_length = out[0:1, 38:46]
    duration_type = out[0:1, 46:]
    pitch_index = tf.multinomial(pitch / temperature, 1)
    delta_time_length_index = tf.multinomial(
        delta_time_length / temperature, 1
    )
    delta_time_type_index = tf.multinomial(delta_time_type / temperature, 1)
    duration_length_index = tf.multinomial(duration_length / temperature, 1)
    duration_type_index = tf.multinomial(duration_type / temperature, 1)
    print(pitch_index.shape, delta_time_length_index.shape, delta_time_type_index.shape, duration_length_index.shape, duration_type_index.shape)
    new_pitch = tf.one_hot(pitch_index, 27)
    new_delta_time_length = tf.one_hot(delta_time_length_index, 8)
    new_delta_time_type = tf.one_hot(delta_time_type_index, 3)
    new_duration_length = tf.one_hot(duration_length_index, 8)
    new_duration_type = tf.one_hot(duration_type_index, 3)
    print(new_pitch.shape, new_delta_time_length.shape, new_delta_time_type.shape, new_duration_length.shape, new_duration_type.shape)
    generated_out = tf.concat(
        [
            new_pitch,
            new_delta_time_length,
            new_delta_time_type,
            new_duration_length,
            new_duration_type
        ],
        2
    )
    print(generated_out.shape)
    return generated_out[0], generation_sstate


if __name__ == "__main__":

    # Read data.
    file = open("../binge_and_grab.notes", "rb")
    notes_type, matrix_wrap, notes_frame_width = file_io.read_notes_header(file)
    if notes_type == notes_handling.GUITAR_NOTE:
        note_vector_length = notes_handling.GUITAR_PITCH_VECTOR_LENGTH + \
                             2 * notes_handling.TIME_VECTOR_LENGTH
    else:
        note_vector_length = notes_handling.DRUMS_PITCH_VECTOR_LENGTH + \
                             2 * notes_handling.TIME_VECTOR_LENGTH
    notes_matrix = np.fromfile(file).reshape([-1, note_vector_length])
    print(notes_matrix.shape)

    # Placeholders for rnn.
    train_in = tf.placeholder(
        dtype=tf.float32, shape=[TRAIN_ROLL_OUT, DRUMS_NOTE_LENGTH]
    )
    generation_in = tf.placeholder(
        dtype=tf.float32, shape=[1, DRUMS_NOTE_LENGTH]
    )
    previous_state = tf.placeholder(
        dtype=tf.float32,
        shape=[NUMBER_OF_LAYERS, STATES_PER_LAYER, 1, HIDDEN_SIZE]
    )
    learning_rate = tf.placeholder(
        dtype=tf.float32,
        shape=[]
    )
    softmax_temperature = tf.placeholder(dtype=tf.float32, shape=[])

    cell, out_weights, out_biases = create_cell(DRUMS_NOTE_LENGTH, HIDDEN_SIZE)
    loss, train, state = create_train_graph(
        cell, out_weights, out_biases, TRAIN_ROLL_OUT,
        train_in, previous_state, learning_rate
    )
    gen_out, gen_state = create_generation_graph(
        cell, out_weights, out_biases,
        generation_in, previous_state, softmax_temperature
    )

    session = tf.Session()
    session.run(tf.global_variables_initializer())

    track_i = 0
    notes_i = 0
    history_state = np.zeros(
        [NUMBER_OF_LAYERS, STATES_PER_LAYER, 1, HIDDEN_SIZE]
    )
    gen_output = np.zeros([GENERATION_ROLL_OUT + 1, 49])
    current_track = notes_matrix
    smooth_loss = (-np.log(1.0 / 27) - np.log(1.0/11) - np.log(1.0/11))
    temps = [0.001, 2./6., 3./6., 4./6.]
    temps_i = 0
    for i in range(100000):

        if i % 100 == 0:
            temps_i = (temps_i + 1) % 3
            generation_state = history_state
            gen_output[0] = notes_matrix[notes_i]
            for j in range(1, GENERATION_ROLL_OUT + 1):
                gen_output[j], generation_state = session.run(
                    [gen_out, gen_state],
                    feed_dict={
                        generation_in: gen_output[j - 1:j],
                        previous_state: generation_state,
                        softmax_temperature: temps[temps_i]
                    }
                )
            notes = []
            for j in range(gen_output.shape[0]):
                notes.append(
                    notes_handling.create_note_from_vector(
                        notes_handling.DRUMS_NOTE, gen_output[j]
                    )
                )
            notes_file = open(
                "../../data/outs/sample_{}_{}.notes".format(i // 100, temps_i), "wb"
            )
            file_io.write_notes_file(
                notes_file, notes_handling.DRUMS_NOTE, 1, 1, notes
            )
            notes_file.close()
        else:
            loss_value, _, history_state = session.run(
                [loss, train, state],
                feed_dict={
                    train_in: notes_matrix[notes_i:notes_i + TRAIN_ROLL_OUT],
                    previous_state: history_state,
                    learning_rate: 0.001
                }
            )
            smooth_loss = smooth_loss * 0.999 + loss_value * 0.001

        print(i, smooth_loss)

        notes_i += TRAIN_ROLL_OUT
        if notes_i + TRAIN_ROLL_OUT > current_track.shape[0]:
            notes_i = 0
            history_state = np.zeros(
                [NUMBER_OF_LAYERS, STATES_PER_LAYER, 1, HIDDEN_SIZE]
            )
