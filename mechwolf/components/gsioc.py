try:
    import serial
except ImportError:
    pass

from time import sleep


class GsiocComponent:
    def __init__(self, serial_port=None, unit_id=0):
        self.ser = serial.Serial(
            serial_port, baudrate=19200, parity="E", stopbits=1, timeout=0.02
        )

        self.gsioc_id = 0x80 + unit_id

        self.version = self.immediate_command("%")

    def __del__(self):
        self.ser.close()

    def reset(self):
        self.immediate_command("$")

    def disconnect(self):
        # disconnect all slaves
        self.ser.write([0xFF])
        # give slaves time to disconnect
        sleep(0.02)
        self.ser.reset_input_buffer()

    def connect(self):

        self.disconnect()
        # connect slave with this ID
        max_try = 3
        for i in range(max_try):
            self.ser.write([self.gsioc_id])
            response = self.ser.read()
            if response == bytes([self.gsioc_id]):
                return True

        raise RuntimeError(
            "Device with ID {} did not respond.".format(self.gsioc_id - 128)
        )

    def immediate_command(self, command):
        self.connect()
        response = ""

        self.ser.write(command.encode(encoding="ascii"))

        char = self.ser.read()

        while char < b"\x80":
            response += char.decode(encoding="ascii")
            self.ser.write([0x06])
            char = self.ser.read()

        return response

    def buffered_command(self, command):
        self.connect()

        response = b""

        # waiting for slave to be ready
        while response != b"\n":
            self.ser.write([0x0A])
            response = self.ser.read()

        # slave should echo each char back to us
        # we terminate command with a \r

        for char in command + "\r":
            byte = char.encode(encoding="ascii")
            self.ser.write(byte)
            char = self.ser.read()

            if len(char) < 1 or char != byte:
                raise RuntimeError(
                    "Device did not respond to buffered command.".format(
                        self.gsioc_id - 128
                    )
                )

        return response
