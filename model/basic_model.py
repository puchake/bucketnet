""" This module contains basic model definition. """


import tensorflow as tf
import numpy as np

from model.building import *
from model.composer import Composer
from processing.dataset import Dataset


class BasicModel:
    """ Basic model described in the sentiment analysis tutorial. """

    # Mapping of run types used through the model to dataset subsets constants.
    RUN_TYPES_TO_SETS = {"train": Dataset.TRAIN, "validation": Dataset.VAL,
                         "test": Dataset.TEST}

    def __init__(self, build_params, train_root, val_root, checkpoints_root,
                 best_model_root):
        self._create_paths(train_root, val_root, checkpoints_root,
                           best_model_root)
        self._create_placeholders(**build_params)
        self._build_net(**build_params)
        self._build_training_nodes(build_params["charset_size"])
        self._create_summary()
        self._create_environment()
        self._register_infer_nodes()

    def train(
            self, dataset, learning_rate=0.001, desired_loss=0.001,
            max_iterations=1000000, decay_interval=10, decay_rate=1.0,
            save_interval=1000, best_save_interval=200,
            validation_interval=200, lstm_dropout=0.0, batch_size=50,
            max_patience=20, early_stopping=False, charset_size=102
    ):
        """ Public entry point for model's training. """
        self._session.run(tf.global_variables_initializer())
        min_loss = -np.log(1 / charset_size)
        patience = max_patience
        train_state = self._create_state_matrix(batch_size)
        for iteration in range(max_iterations):
            train_loss_out, _ = self._do_single_run(
                "train", iteration, dataset, batch_size, learning_rate,
                lstm_dropout, train_state, loops_limit=10
            )
            if iteration % validation_interval == 0:
                val_loss_out, _ = self._do_single_run(
                    "validation", iteration, dataset, batch_size, 0.0, 0.0
                )
                if val_loss_out < min_loss:
                    patience = max_patience
                else:
                    patience -= 1
            if iteration % decay_interval == 0:
                learning_rate *= decay_rate
            if iteration % save_interval == 0:
                self._checkpoints_saver.save(
                    self._session, self._checkpoint_file_path,
                    global_step=iteration
                )
            # Save best model basing on validation loss.
            if iteration % best_save_interval == 0 and val_loss_out < min_loss:
                min_loss = val_loss_out
                self._best_model_saver.save(self._session,
                                            self._best_model_file_path)
            if train_loss_out < desired_loss:
                break
            # Early stopping.
            if early_stopping and patience == 0:
                break
        self._best_model_saver.restore(self._session,
                                       self._best_model_file_path)
        final_loss, final_accuracy = self._do_single_run(
            "test", -1, dataset, batch_size, 0.0, 0.0
        )
        return final_loss, final_accuracy

    def _do_single_run(self, run_type, iteration, dataset, batch_size,
                       learning_rate, lstm_dropout, state=None,
                       loops_limit=None):
        """ Perform single run of selected type. """
        losses = []
        accuracies = []
        # Determine which nodes to run and set index.
        nodes_to_run = [self._loss, self._accuracy, self._out_state]
        if run_type == "train":
            nodes_to_run += [self._train]
        set_index = self.RUN_TYPES_TO_SETS[run_type]
        keep_running = True
        loops_count = 0
        # Construct state if needed.
        if state is None:
            state = self._create_state_matrix(batch_size)
        while keep_running:
            data, queue_reset = dataset.get_next_batch(set_index, state)
            output = self._session.run(
                nodes_to_run,
                feed_dict={self._in_data: data,
                           self._in_state: state,
                           self._in_lstm_dropout: lstm_dropout,
                           self._in_learning_rate: learning_rate}
            )
            # Unpack loss and accuracy from run output.
            loss, accuracy, out_state = output[:3]
            state = np.array(out_state)
            losses.append(loss)
            accuracies.append(accuracy)
            loops_count += 1
            if run_type == "train":
                keep_running = loops_count < loops_limit
            else:
                # On validation and test runs iterate over whole subset.
                keep_running = not queue_reset
        # Log obtained loss and accuracy values.
        mean_loss = np.mean(losses)
        mean_accuracy = np.mean(accuracies)
        self._output_summary(run_type, iteration, mean_loss, mean_accuracy)
        return mean_loss, mean_accuracy

    def _output_summary(self, run_type, iteration, loss, accuracy):
        """ Output loss and accuracy summary to selected writer. """
        summary_out, = self._session.run(
            [self._summary],
            feed_dict={self._in_loss: loss, self._in_accuracy: accuracy}
        )
        if run_type == "train":
            self._train_writer.add_summary(summary_out, global_step=iteration)
        elif run_type == "validation":
            self._val_writer.add_summary(summary_out, global_step=iteration)

    def _create_state_matrix(self, batch_size):
        """ Create matrix which can hold model's state. """
        state_shape = self._in_state.shape.as_list()
        state_shape[2] = batch_size
        state = np.zeros(state_shape)
        return state

    # Building routines.

    def _create_paths(self, train_root, val_root, checkpoints_root,
                      best_model_root):
        """ Initialize paths used by model. """
        self._train_root = train_root
        self._val_root = val_root
        self._checkpoints_root = checkpoints_root
        self._best_model_root = best_model_root
        self._checkpoint_file_path = self._checkpoints_root + "/model"
        self._best_model_file_path = self._best_model_root + "/model"

    def _create_placeholders(self, layers_count=3, layers_size=512, roll_out=20,
                             charset_size=102):
        """ Create necessary model's placeholders. """
        self._in_data = tf.placeholder(tf.float32,
                                       shape=[roll_out, None, charset_size])
        self._in_generation_data = tf.placeholder(tf.float32,
                                                  shape=[None, charset_size])
        self._in_state = tf.placeholder(
            tf.float32, shape=[layers_count, 2, None, layers_size]
        )
        self._in_temperature = tf.placeholder(tf.float32, shape=[])
        self._in_learning_rate = tf.placeholder(tf.float32, shape=[])
        self._in_lstm_dropout = tf.placeholder(tf.float32, shape=[])

    def _build_net(self, layers_count=3, layers_size=512, roll_out=20,
                   charset_size=102):
        """ Build whole network. """
        cell = build_lstm_cell(layers_count, layers_size, self._in_lstm_dropout)
        out_weights, out_biases = build_linear_layer("out", layers_size,
                                                     charset_size)
        self._final_outs, self._out_state = build_train_graph(
            cell, out_weights, out_biases, self._in_state, self._in_data,
            roll_out, charset_size
        )
        self._generated_symbols, self._generated_state = build_generation_graph(
            cell, out_weights, out_biases, self._in_state,
            self._in_generation_data, self._in_temperature
        )

    def _build_training_nodes(self, charset_size):
        """ Create training nodes. """
        logits = tf.reshape(self._final_outs[:-1], [-1, charset_size])
        labels = tf.reshape(self._in_data[1:], [-1, charset_size])
        self._loss = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(logits=logits,
                                                    labels=labels)
        )
        self._accuracy = tf.reduce_mean(
            tf.cast(tf.equal(tf.argmax(logits, 1), tf.argmax(labels, 1)),
                    dtype=tf.float32)
        )
        self._train = tf.train.AdamOptimizer(
            learning_rate=self._in_learning_rate
        ).minimize(self._loss)

    def _create_summary(self):
        """ Create train and validation summary nodes. """
        self._in_loss = tf.placeholder(tf.float32, [])
        self._in_accuracy = tf.placeholder(tf.float32, [])
        tf.summary.scalar("loss", self._in_loss)
        tf.summary.scalar("accuracy", self._in_accuracy)
        self._summary = tf.summary.merge_all()

    def _create_environment(self):
        """ Create training environment. """
        self._session = tf.Session()
        self._best_model_saver = tf.train.Saver(max_to_keep=1)
        self._checkpoints_saver = tf.train.Saver(max_to_keep=10)
        self._train_writer = tf.summary.FileWriter(self._train_root)
        self._val_writer = tf.summary.FileWriter(self._val_root)

    def _register_infer_nodes(self):
        """ Register graph nodes used in classification with trained model. """
        tf.add_to_collection(Composer.IN_GENERATION_DATA,
                             self._in_generation_data)
        tf.add_to_collection(Composer.IN_GENERATION_STATE, self._in_state)
        tf.add_to_collection(Composer.IN_TEMPERATURE, self._in_temperature)
        tf.add_to_collection(Composer.IN_LSTM_DROPOUT, self._in_lstm_dropout)
        tf.add_to_collection(Composer.GENERATED_SYMBOLS,
                             self._generated_symbols)
        self._register_generated_state()

    def _register_generated_state(self):
        """
        LSTM state needs to be registered in a special way in a collection.
        """
        for layer_state in self._generated_state:
            tf.add_to_collection(Composer.GENERATED_STATE, layer_state.c)
            tf.add_to_collection(Composer.GENERATED_STATE, layer_state.h)
