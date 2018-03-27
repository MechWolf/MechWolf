import serial
from .valve import Valve

class ViciValve(Valve):
    '''Controls a VICI Valco Valve'''

    def __init__(self, mapping={}, name=None, serial_port=None, positions=10):
        super().__init__(mapping=mapping, name=name)

        self.serial_port = serial_port
        self.positions = positions

    def __enter__(self):
        self.ser = serial.Serial(self.serial_port, 115200, parity=serial.PARITY_NONE, stopbits=1, timeout=0.1)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()
        return self

    def get_position(self):
        self.ser.write(b'CP\r')
        response = self.ser.readline()
        if response:
            position = int(response[2:4]) # Response is in the form 'CPXX\r'
            return position
        else:
            return False
