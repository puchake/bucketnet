from io import BytesIO
import struct


class MidiBytesIO (BytesIO):
    """
    BytesIO extension class with methods for reading values from midi file.
    """

    # Constants defining chunk header, int and short sizes used in midi file.
    HEADER_SIZE = 4
    INT_SIZE = 4
    SHORT_SIZE = 2

    # Constant, valid file chunks headers.
    HEADER_HEADER = b'MThd'
    TRACK_HEADER = b'MTrk'

    # Constants used in variable length quantity reading.
    VALUE_BITS_PER_VLQ_BYTE = 7
    MAX_VALUE_IN_VQL_BYTE = 127
    VLQ_CONTINUATION_BIT = 0b10000000

    def __init__(self, source_bytes):
        super().__init__(source_bytes)

    def read_header(self):
        """
        Read next HEADER_SIZE bytes from byte buffer.

        :return: Read bytes.
        """

        return self.read(MidiBytesIO.HEADER_SIZE)

    def write_header(self, header):
        """
        Write HEADER_SIZE header's bytes to byte buffer.

        :param header: header's bytes
        :return: -
        """

        self.write(header)

    def read_int(self):
        """
        Read next INT_SIZE bytes from byte buffer.
        Treat them as int saved in MSB first order.

        :return: read int value
        """

        int_bytes = self.read(MidiBytesIO.INT_SIZE)
        return struct.unpack(">I", int_bytes)[0]

    def write_int(self, value):
        """
        Write int value bytes to byte buffer in MSB first order.

        :param value: value of saved int
        :return: -
        """

        int_bytes = struct.pack(">I", value)
        self.write(int_bytes)

    def read_short(self):
        """
        Read next SHORT_SIZE bytes from byte buffer.
        Treat them as short saved in MSB first order.

        :return: read short value
        """

        short_bytes = self.read(MidiBytesIO.SHORT_SIZE)
        return struct.unpack(">H", short_bytes)[0]

    def write_short(self, value):
        """
        Write short value bytes to byte buffer in MSB first order.

        :param value: value of saved short
        :return: -
        """

        short_bytes = struct.pack(">H", value)
        self.write(short_bytes)

    def read_byte(self):
        """
        Read next byte from byte buffer.

        :return: read byte numeric value
        """

        return self.read(1)[0]

    def write_byte(self, value):
        """
        Write single byte to byte buffer.

        :param value: numeric value of saved byte
        :return: -
        """

        self.write(bytes([value]))

    def read_vlq(self):
        """
        Read next value from byte buffer,
        which is saved in variable length quantity format.

        :return: read variable length quantity value
        """

        # Read first byte from byte buffer and save its value bits in value.
        byte = self.read(1)[0]
        value = byte & MidiBytesIO.MAX_VALUE_IN_VQL_BYTE

        # While read byte has its MS bit set to 1:
        while byte & MidiBytesIO.VLQ_CONTINUATION_BIT != 0:

            # Shift value VALUE_BITS_PER_VLQ_BYTE bits to the left,
            # read next byte and add its value bits to value.
            value <<= MidiBytesIO.VALUE_BITS_PER_VLQ_BYTE
            byte = self.read(1)[0]
            value += byte & MidiBytesIO.MAX_VALUE_IN_VQL_BYTE

        return value

    def write_vlq(self, value):
        """
        Write value to byte buffer in variable length quantity format.

        :param value: saved value
        :return: -
        """

        # Save first vlq byte to array and
        # shift value VALUE_BITS_PER_VLQ_BYTE to the right.
        vlq_bytes = bytes([value & MidiBytesIO.MAX_VALUE_IN_VQL_BYTE])
        value >>= MidiBytesIO.VALUE_BITS_PER_VLQ_BYTE

        # While there are bits left in value which need to be saved:
        while value > 0:

            # Save next vq byte in byte array,
            # but this time with its continuation bit set.
            # Shift value VALUE_BITS_PER_VLQ_BYTE bits more to the right.
            vlq_bytes += bytes(
                             [
                                 MidiBytesIO.VLQ_CONTINUATION_BIT |
                                 (value & MidiBytesIO.MAX_VALUE_IN_VQL_BYTE)
                             ]
                         )
            value >>= MidiBytesIO.VALUE_BITS_PER_VLQ_BYTE

        # Write saved bytes in reverse order.
        self.write(vlq_bytes[::-1])
