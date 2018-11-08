from .pump import Pump
from . import ureg
import time

from .gsioc import GsiocComponent

class VarianPump(Pump):
    '''A Varian pump.
    Unit id is the Unit id that is configurable on device
    '''

    def __init__(self, name, serial_port=None, max_rate=0, unit_id=0):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self.max_rate = max_rate
        self.serial_port = serial_port
        self.unit_id = unit_id

    def __enter__(self):
        self.gsioc = GsiocComponent(serial_port=self.serial_port, unit_id=self.unit_id)

        self.lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unlock()

    def lock(self):
        self.gsioc.buffered_command('L')

    def unlock(self):
        self.gsioc.buffered_command('U') # unlock keypad
        self.gsioc.buffered_command('W') # release display

    def set_flow(self, flow_rate):

        # Varian pumps will not accept commands unless keypad is locked
        # If operator power cycles the pump between protocols, the lock is lost
        # So we lock the device before each command just to make sure
        self.lock()

        # Flow rate must be supplied as a string from 000000 to 100000, where 100000 = 100% of the maximum pump flow rate.
        percentage = 100000 * flow_rate / self.max_rate

        flow_command = 'X' + str(int(percentage)).zfill(6)

        print('Setting flow rate to {} using command {}'.format(flow_rate, flow_command))

        self.gsioc.buffered_command(flow_command)

        if flow_rate > 0:
            # If we are flowing, we print mechwolf parameters on the display
            self.gsioc.buffered_command('W0=        MechWolf')
            self.gsioc.buffered_command('W1=       {} ml/min'.format(flow_rate))
        else:
            # If we are not flowing, we unlock the keypad and release the display
            # so the operator can intervene (e.g prime)
            self.unlock()

    async def update(self):
        new_rate = ureg.parse_expression(self.rate).to(ureg.ml / ureg.min).magnitude
        self.set_flow(new_rate)
        yield { "timestamp": time.time(),
                "payload": {"rate": str(new_rate)},
                "type": 'log'}

    def config(self):
        #TODO Make max_rate a ureg?
        return dict(serial_port=(str, None), max_rate=(int, None), unit_id=(int, 0))
