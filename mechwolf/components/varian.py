from .pump import Pump
from . import ureg

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
        self.unit_id=unit_id

    def __enter__(self):

        self.gsioc = GsiocComponent(serial_port=self.serial_port, unit_id=self.unit_id)

        self.lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unlock()

    def lock(self):
        self.gsioc.buffered_command('L')

    def unlock(self) :
        self.gsioc.buffered_command('U')

    def set_flow(self, flow_rate):
        print(flow_rate)
        #Flow rate must be supplied as an string from 000000 to 100000, where 100000 = 100% of the maximum pump flow rate.
        percentage = 100000 * flow_rate / self.max_rate
        #print(percentage)
        flow_command = 'X'+str(int(percentage)).zfill(6)
        print(flow_command)
        self.gsioc.buffered_command(flow_command)

    async def update(self):
        new_rate = ureg.parse_expression(self.rate).to(ureg.ml / ureg.min).magnitude
        self.set_flow(new_rate)
        yield str(new_rate)

    def config(self):
        #TODO Make max_rate a ureg?
        return dict(serial_port=(str, None), max_rate=(int, None))
