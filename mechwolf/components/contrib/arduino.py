import serial

from ..stdlib.sensor import Sensor


class ArduinoSensor(Sensor):
    """
    Generic driver for an Arduino based sensor
    These devices connect through serial at 115200 baud
    They spit some information upon first connect/reset
    Then they listen for a single byte command
    They spit out some data in ASCII in return.
    """

    metadata = {
        "author": [
            {
                "first_name": "Murat",
                "last_name": "Ozturk",
                "email": "hello@littleblack.fish",
                "institution": "Indiana University, School of Informatics, Computing and Engineering",
                "github_username": "littleblackfish",
            }
        ],
        "stability": "beta",
        "supported": True,
    }

    def __init__(self, name=None, serial_port=None, command="*"):
        super().__init__(name=name)
        self.serial_port = serial_port
        self.command = command.encode(encoding="ASCII")

    def __enter__(self):
        self.ser = serial.Serial(
            self.serial_port, 115200, parity=serial.PARITY_NONE, stopbits=1
        )

        # Listen to sensor's self-introduction
        # (gives it time for internal init)
        self.ser.readline()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # close the serial connection
        self.ser.close()

    def read(self):

        # flush in buffer in case we have stale data
        if self.ser.in_waiting:
            self.ser.reset_input_buffer()

        # send the command
        self.ser.write(self.command)
        # read the data and sanitize
        data = self.ser.readline().decode(encoding="ASCII").strip()

        try:
            # maybe it is a nice integer (straight from ADC)
            return int(data)
        except ValueError:
            # otherwise it is a float
            return float(data)
