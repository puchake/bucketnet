import rnn.rnn_loss as rnn_loss
import midi_io.notes_handling as notes_handling

import unittest
import tensorflow as tf
import numpy as np


class RNNLossTestCase (unittest.TestCase):

    def test_slice_outputs_guitar_note(self):

        # Arrange
        outputs = tf.random_uniform(
            [
                1,
                notes_handling.GUITAR_PITCH_VECTOR_LENGTH +
                2 * notes_handling.TIME_VECTOR_LENGTH
            ]
        )
        expected_pitch_part = outputs[
            :, :notes_handling.GUITAR_PITCH_VECTOR_LENGTH
        ]
        expected_delta_time_part = outputs[
            :,
            notes_handling.GUITAR_PITCH_VECTOR_LENGTH:
            notes_handling.GUITAR_PITCH_VECTOR_LENGTH +
            notes_handling.TIME_VECTOR_LENGTH
        ]
        expected_duration_part = outputs[
             :,
             notes_handling.GUITAR_PITCH_VECTOR_LENGTH +
             notes_handling.TIME_VECTOR_LENGTH:
        ]
        session = tf.Session()

        # Act
        rnn_pitch_part, correct_pitch_part, \
        rnn_delta_time_part, correct_delta_time_part, \
        rnn_duration_part, correct_duration_part = rnn_loss.slice_outputs(
            outputs, outputs, notes_handling.GUITAR_NOTE
        )

        # Assert
        expected,  = session.run([expected_pitch_part, rnn_pitch_part])
        self.assertTrue(
            np.alltrue(
                expected_pitch_part.eval(session=session) ==
                rnn_pitch_part.eval(session=session)
            )
        )



if __name__ == '__main__':
    unittest.main()
