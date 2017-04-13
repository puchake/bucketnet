from src.midi_io.utilities.MidiBytesIO import MidiBytesIO

import unittest


class MidiBytesIOTestCase(unittest.TestCase):

    def test_read_vlq_1_byte(self):

        # Arrange
        vlq_bytes = b'\x0A'
        source = MidiBytesIO(vlq_bytes)

        # Act
        value = source.read_vlq()

        # Assert
        self.assertEqual(value, 0x0A)

    def test_read_vlq_2_byte(self):

        # Arrange
        vlq_bytes = b'\xF3\x0A'
        source = MidiBytesIO(vlq_bytes)

        # Act
        value = source.read_vlq()

        # Assert
        self.assertEqual(value, 0x398A)

    def test_read_vlq_3_byte(self):

        # Arrange
        vlq_bytes = b'\xF8\x87\x0C'
        source = MidiBytesIO(vlq_bytes)

        # Act
        value = source.read_vlq()

        # Assert
        self.assertEqual(value, 0x1E038C)

    def test_read_vlq_4_byte(self):

        # Arrange
        vlq_bytes = b'\xFF\xFF\xFF\x7F'
        source = MidiBytesIO(vlq_bytes)

        # Act
        value = source.read_vlq()

        # Assert
        self.assertEqual(value, 0xFFFFFFF)

    def test_write_vlq_1_byte(self):

        # Arrange
        vlq_value = 0x0A
        destination = MidiBytesIO(b'')

        # Act
        destination.write_vlq(vlq_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\x0A')

    def test_write_vlq_2_byte(self):

        # Arrange
        vlq_value = 0x398A
        destination = MidiBytesIO(b'')

        # Act
        destination.write_vlq(vlq_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\xF3\x0A')

    def test_write_vlq_3_byte(self):

        # Arrange
        vlq_value = 0x1E038C
        destination = MidiBytesIO(b'')

        # Act
        destination.write_vlq(vlq_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\xF8\x87\x0C')

    def test_write_vlq_4_byte(self):

        # Arrange
        vlq_value = 0xFFFFFFF
        destination = MidiBytesIO(b'')

        # Act
        destination.write_vlq(vlq_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\xFF\xFF\xFF\x7F')

    def test_read_byte(self):

        # Arrange
        byte = b'\x30'
        source = MidiBytesIO(byte)

        # Act
        byte_value = source.read_byte()

        # Assert
        self.assertEqual(byte_value, 0x30)

    def test_read_short(self):

        # Arrange
        short_bytes = b'\xAB\xCD'
        source = MidiBytesIO(short_bytes)

        # Act
        short_value = source.read_short()

        # Assert
        self.assertEqual(short_value, 0xABCD)

    def test_read_int(self):

        # Arrange
        int_bytes = b'\x12\x34\x56\x78'
        source = MidiBytesIO(int_bytes)

        # Act
        int_value = source.read_int()

        # Assert
        self.assertEqual(int_value, 0x12345678)

    def test_read_header(self):

        # Arrange
        header_bytes = b'MTrk'
        source = MidiBytesIO(header_bytes)

        # Act
        read_header_bytes = source.read_header()

        # Assert
        self.assertEqual(read_header_bytes, header_bytes)

    def test_write_byte(self):

        # Arrange
        byte_value = 0x30
        destination = MidiBytesIO(b'')

        # Act
        destination.write_byte(byte_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\x30')

    def test_write_short(self):

        # Arrange
        short_value = 0x3456
        destination = MidiBytesIO(b'')

        # Act
        destination.write_short(short_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\x34\x56')

    def test_write_int(self):

        # Arrange
        int_value = 0x3456789A
        destination = MidiBytesIO(b'')

        # Act
        destination.write_int(int_value)

        # Assert
        self.assertEqual(destination.getbuffer(), b'\x34\x56\x78\x9A')

    def test_write_header(self):

        # Arrange
        header_bytes = b'MThd'
        destination = MidiBytesIO(b'')

        # Act
        destination.write_header(header_bytes)

        # Assert
        self.assertEqual(destination.getbuffer(), header_bytes)


if __name__ == '__main__':
    unittest.main()
