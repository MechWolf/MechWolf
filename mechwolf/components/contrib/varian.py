from ..stdlib.pump import Pump
from . import _ureg


class VarianPump(Pump):
    """
    A Varian pump

    This is the GSIOC based Varian pump driver.
    This pump is characterized by the maximum flow rate of the installed head.

    Arguments:
    - `serial_port`: Serial port through which device is connected
    - `max_rate`: Maximum flow rate (of the installed head) e.g. '5 ml/min'
    - `unit_id`: The GSIOC unit ID set on device (0 by default)
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

    def __init__(self, serial_port, max_rate, unit_id=0, name=None):
        super().__init__(name=name)
        self.rate = _ureg.parse_expression("0 ml/min")
        self.max_rate = _ureg.parse_expression(max_rate)
        self.serial_port = serial_port
        self.unit_id = unit_id

    def __enter__(self):
        from .gsioc import GsiocInterface

        self._gsioc = GsiocInterface(serial_port=self.serial_port, unit_id=self.unit_id)

        self._lock()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.rate = _ureg.parse_expression("0 mL/min")
        # Stop pump
        self._gsioc.buffered_command("X000000")
        self._unlock()
        del self._gsioc

    def _lock(self):
        self._gsioc.buffered_command("L")
        # self._gsioc.buffered_command("W0=        MechWolf")

    def _unlock(self):
        self._gsioc.buffered_command("U")  # unlock keypad
        self._gsioc.buffered_command("W")  # release display

    async def _set_flow(self, flow_rate):

        max_rate = self.max_rate.to(_ureg.ml / _ureg.min).magnitude

        # Flow rate must be supplied as a string from 000000 to 100000
        # where 100000 = 100% of the maximum pump flow rate.
        percentage = 100000 * flow_rate / max_rate

        flow_command = "X" + str(int(percentage)).zfill(6)

        await self._gsioc.buffered_command_async(flow_command)

        # await self._gsioc.buffered_command_async(
        #    "W1=       {} ml/min".format(flow_rate)
        # )

    async def _update(self) -> None:
        new_rate = self.rate.to(_ureg.ml / _ureg.min).magnitude
        await self._set_flow(new_rate)
