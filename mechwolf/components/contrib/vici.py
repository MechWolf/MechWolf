# NOTE: When changing this file, be sure to update new_components.rst
# because it references specific line numbers here.
try:
    import serial
except ImportError:
    pass

from ..stdlib.valve import Valve


class ViciValve(Valve):
    """Controls a VICI Valco Valve"""

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

    def __init__(self, name=None, mapping={}, serial_port=None):
        super().__init__(name=name, mapping=mapping)
        self.serial_port = serial_port

    def __enter__(self):
        # create the serial connection
        self.ser = serial.Serial(
            self.serial_port,
            9600,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=0.1,
            write_timeout=0.1,
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # close the serial connection
        self.ser.close()

    def get_position(self):
        """Returns the position of the valve.

        Note:
            This method was used for introspection and debugging.
            It is preserved but not currently used by any MechWolf function.

        Returns:
            int: The position of the valve.
        """
        self.ser.write(b"CP\r")
        response = self.ser.readline()
        if response:
            position = int(response[2:4])  # Response is in the form 'CPXX\r'
            return position
        return False

    def update(self):
        message = f"GO{self.setting}\r"
        self.ser.write(message.encode())  # send the message to the valve
        # print(self.setting) # for introspection
        return True
