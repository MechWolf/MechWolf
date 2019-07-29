from ..stdlib.pump import Pump
from . import ureg

class VarianPump(Pump):
    """A Varian pump.

    This is the GSIOC based Varian pump driver.
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

    def __init__(self, name, serial_port=None, max_rate="0 mL/min", unit_id=0):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self.max_rate = ureg.parse_expression(max_rate)
        self.serial_port = serial_port
        self.unit_id=unit_id

    def __enter__(self):

        from .gsioc import GsiocInterface

        self.gsioc = GsiocInterface(serial_port=self.serial_port, unit_id=self.unit_id)

        self.lock()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.rate = ureg.parse_expression("0 mL/min")
        self.update()
        self.unlock()
        del self.gsioc

    def lock(self):
        self.gsioc.buffered_command('L')
        self.gsioc.buffered_command('W0=        MechWolf')

    def unlock(self) :
        self.gsioc.buffered_command('U') # unlock keypad
        self.gsioc.buffered_command('W') # release display

    async def set_flow(self, flow_rate):

        max_rate = self.max_rate.to(ureg.ml / ureg.min).magnitude

        # Flow rate must be supplied as a string from 000000 to 100000
        # where 100000 = 100% of the maximum pump flow rate.
        percentage = 100000 * flow_rate / max_rate

        flow_command = 'X'+str(int(percentage)).zfill(6)

        await self.gsioc.buffered_command_async(flow_command)

        await self.gsioc.buffered_command_async('W1=       {} ml/min'.format(flow_rate))


    async def update(self) -> None:
        new_rate = self.rate.to(ureg.ml / ureg.min).magnitude
        await self.set_flow(new_rate)
