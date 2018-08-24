from .pump import Pump
from . import ureg

try:
    import serial
except ImportError:
    pass

class VarianPump(Pump):
    '''A Varian pump.
    '''

    def __init__(self, name, serial_port=None, max_rate=0):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self.max_rate = max_rate
        self.serial_port = serial_port

        #VARIAN PUMP SPECIFIC OPTIONS
        #TODO: MAKE THIS A CONGFIGURABLE OPTION
        self.pump_id = 0x80

    def __enter__(self):

        self.ser = serial.Serial(self.serial_port)
        self.ser.baudrate = 19200
        self.ser.parity = 'E'
        self.ser.stopbits = 1
        self.ser.timeout = 1
        self.lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()

    def lock(self):
        lock_command = [0xFF, self.pump_id, 0x0A, 0x4C, 0x0D]
        self.ser.write(lock_command)
        print(self.ser.read_all())

    def set_flow(self, flow_rate):
        print(flow_rate)
        #Flow rate must be supplied as an string from 000000 to 100000, where 100000 = 100% of the maximum pump flow rate.
        percentage = 100000 * flow_rate / self.max_rate
        print(percentage)
        flow_command = [0xFF, self.pump_id, 0x0A, 0x58]
        flow_command.extend(list(str(int(percentage)).zfill(6).encode()))
        flow_command.append(0x0D)
        print(flow_command)
        self.ser.write(flow_command)
        print(self.ser.read_all())

    async def update(self):
        new_rate = ureg.parse_expression(self.rate).to(ureg.ml / ureg.min).magnitude
        self.set_flow(new_rate)
        yield str(new_rate)

    def config(self):
        #TODO Make max_rate a ureg?
        return dict(serial_port=(str, None), max_rate=(int, None))
