from ..stdlib.valve import Valve

class ViciValve(Valve):
    """Controls a VICI Valco Valve"""

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

    def __init__(self, name=None, mapping={}, serial_port=None):
        super().__init__(name=name, mapping=mapping)
        self.serial_port = serial_port

    def __enter__(self):
        import aioserial

        # create the serial connection
        self.ser = aioserial.AioSerial(
            self.serial_port,
            9600,
            parity=aioserial.PARITY_NONE,
            stopbits=1,
            timeout=0.2,
            write_timeout=0.1 )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # close the serial connection
        del self.ser

    def get_position(self):
        """Returns the position of the valve.

        Note:
            This method was used for introspection and debugging.
            It is preserved but not currently used by any MechWolf function.
            Note that this needs about 200 ms after the last GO command.

        Returns:
            int: The position of the valve.
        """
        self.ser.reset_input_buffer()

        self.ser.write(b'CP\r')
        response = self.ser.readline()

        if response:
            position = int(response[2:4])  # Response is in the form 'CPXX\r'
            return position
        return False

    async def go(self, position) :
        command = f"GO{position}\r"
        await self.ser.write_async(command.encode())

    async def update(self):
        await self.go(self.setting)
