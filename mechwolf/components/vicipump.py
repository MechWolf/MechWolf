from .pump import Pump
from . import ureg

try:
    import serial
except ImportError:
    pass

class ViciPump(Pump):
    '''A Vici M50 pump.
    This pump is characterized by the volume of fluid dispensed per revolution
    which can be found on the certificate of confirmance
    '''

    def __init__(self, name, serial_port=None, volume_per_rev=0):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self.serial_port = serial_port
        self.volume_per_rev = volume_per_rev

    def __enter__(self):

        self.ser = serial.Serial(self.serial_port,
                                 9600,
                                 parity=serial.PARITY_NONE,
                                 stopbits=1,
                                 timeout=0.1,
                                 write_timeout=0.1)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()

    def set_flow(self, flow_rate):

        steps_per_rev = 51200
        gear_ratio = 9.86

        steps_per_second = steps_per_rev / self.volume_per_rev
        steps_per_second *= flow_rate.to(ureg.ml / ureg.sec).magnitude
        steps_per_second *= gear_ratio
        steps_per_second = int(steps_per_second)

        flow_command = 'SL {}\r\n'.format(steps_per_second)

        flow_rate_readable = flow_rate.to(ureg.ml / ureg.min).magnitude

        print("Setting flow rate to {} ml/min using command {}".format(flow_rate_readable, flow_command))

        self.ser.write(flow_command.encode(encoding='ascii'))

        self.ser.reset_input_buffer()

    async def update(self):

        new_rate = ureg.parse_expression(self.rate)

        self.set_flow(new_rate)
        yield str(new_rate)

    def config(self):
        return dict(serial_port=(str, None), volume_per_rev=(float, None))
