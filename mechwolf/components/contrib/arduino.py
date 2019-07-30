from ..stdlib.sensor import Sensor


class ArduinoSensor(Sensor):
    """
    Generic driver for an Arduino based sensor.

    These devices connect through serial at 115200 baud
    They introduce themselves upon first connect/reset
    They listen for a single byte command in the main loop().
    When commanded, they respond with some ASCII data.

    Arguments:

    - `serial_port`: Serial port through which device is connected
    - `command` : Command to be sent to device to request reading. '*' by default.

    Returns:

    ArduinoSensor.read() returns the parsed response, type can be int or float.

    """

    metadata = {
        "author": [
            {
                "first_name": "Murat",
                "last_name": "Ozturk",
                "email": "muzcuk@gmail.com",
                "institution": "Indiana University, School of Informatics, Computing and Engineering",
                "github_username": "littleblackfish",
            }
        ],
        "stability": "beta",
        "supported": True,
    }

    def __init__(self, serial_port, name=None, command="*"):
        super().__init__(name=name)
        self.serial_port = serial_port
        self.command = command.encode(encoding="ASCII")

    def __enter__(self):
        import aioserial

        self.ser = aioserial.AioSerial(
            self.serial_port, 115200, parity=aioserial.PARITY_NONE, stopbits=1
        )

        # Listen to sensor's self-introduction
        # (gives it time for internal init)
        self.ser.readline()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Delete the serial object to the object remains pickleable
        # when it is out of context
        del self.ser

    async def read(self):

        # flush in buffer in case we have stale data
        self.ser.reset_input_buffer()

        # send the command
        await self.ser.write_async(self.command)
        # read the data and sanitize
        data = await self.ser.readline_async()
        data = data.decode(encoding="ASCII").strip()

        try:
            # maybe it is a nice integer (straight from ADC)
            return int(data)
        except ValueError:
            # otherwise it is a float
            return float(data)
