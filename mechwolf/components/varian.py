from .pump import Pump
from . import ureg
import time

try:
    import serial
except ImportError:
    pass

class VarianPump(Pump):
    '''A Varian pump.
    '''

    def __init__(self, name, unit_id='0x80', serial_port=None, max_rate="0 mL/min"):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self.max_rate = ureg.parse_expression(max_rate)
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
        self.set_flow(ureg.parse_expression("0 mL/min").to(ureg.ml/ureg.min).magnitude)
        self.ser.close()

    def lock(self):
        lock_command = [0xFF, self.pump_id, 0x0A, 0x4C, 0x0D]
        self.ser.write(lock_command)
        print(self.ser.read_all())

    def set_flow(self, flow_rate):

        max_rate = self.max_rate.to(ureg.ml / ureg.min).magnitude
        print(f"rate {flow_rate} max_rate {max_rate}")
        #Flow rate must be supplied as an string from 000000 to 100000, where 100000 = 100% of the maximum pump flow rate.
        percentage = 100000 * flow_rate / max_rate
        print(f"percentage {percentage}")
        flow_command = [0xFF, self.pump_id, 0x0A, 0x58]
        flow_command.extend(list(str(int(percentage)).zfill(6).encode()))
        flow_command.append(0x0D)
        print(flow_command)
        self.ser.write(flow_command)

    def update(self):
        print(f"old rate {self.rate}")
        new_rate = self.rate.to(ureg.ml / ureg.min).magnitude
        print(f"new rate {new_rate}")
        self.set_flow(new_rate)
        return { "timestamp": time.time(),
		"params": {"rate": str(new_rate)},
		"device": "self.name"}

    def config(self):
        #TODO Make max_rate a ureg?
        return dict(serial_port=(str, None), max_rate=(int, None))
