from ..stdlib.pump import Pump
from . import _ureg


class HarvardSyringePump(Pump):
    """
    A Harvard Apparatus PHD Ultra syringe pump, used for infusion only.

    The pump has a single pusher block, so every syringe mounted on it moves
    together at the same rate. Commands are sent over the pump's serial (USB)
    connection at 115200 baud. The pump's replies are not read, so a command
    the pump rejects is not reported back.

    Arguments:
    - `syringe_volume`: The volume of the syringe, e.g. `"3 mL"`.
    - `syringe_diameter`: The inner diameter of the syringe, e.g. `"10 mm"`. The pump calculates the flow rate from this value, so it must be correct.
    - `serial_port`: Serial port through which the device is connected (e.g., "COM3" or "/dev/ttyUSB0").
    - `name` (optional): The name of the syringe pump instance. Defaults to `None`.

    Attributes:
    - `serial_port`: The serial port through which the device is connected.
    - `syringe_volume`: The volume of the syringe, parsed into compatible units.
    - `syringe_diameter`: The diameter of the syringe, parsed into compatible units.
    - `_ser`: The `aioserial.AioSerial` object used for asynchronous communication with the pump (created when used as a context manager).
    - `rate`: The current flow rate of the syringe pump (inherited from `mw.Pump`).
    """

    metadata = {
        "author": [
            {
                "first_name": "Prashant",
                "last_name": "Kumar",
                "email": "pprashan@iu.edu",
                "institution": "Indiana University Bloomington, Department of Chemistry",
                "github_username": "Prashant-Kumar-IU",
            },
            {
                "first_name": "Nicola",
                "last_name": "Pohl",
                "email": "npohl@iu.edu",
                "institution": "Indiana University Bloomington, Department of Chemistry",
                "github_username": "NLPohl",
            },
            {
                "first_name": "Murat",
                "last_name": "Ozturk",
                "email": "muzcuk@gmail.com",
                "institution": "Indiana University, School of Informatics, Computing and Engineering",
                "github_username": "littleblackfish",
            },
        ],
        "stability": "beta",
        "supported": True,
    }

    def __init__(self, syringe_volume, syringe_diameter, serial_port, name=None):
        super().__init__(name=name)
        self.serial_port = serial_port
        self.syringe_volume = _ureg.parse_expression(syringe_volume)
        self.syringe_diameter = _ureg.parse_expression(syringe_diameter)

    def __enter__(self):
        import aioserial

        self._ser = aioserial.AioSerial(
            self.serial_port,
            115200,
            parity=aioserial.PARITY_NONE,
            stopbits=1,
            timeout=1,
            write_timeout=1,
        )
        syringe_volume_ml = self.syringe_volume.to(_ureg.ml).magnitude
        syringe_diameter_mm = self.syringe_diameter.to(_ureg.mm).magnitude
        self._ser.write(f"svolume {syringe_volume_ml} ml\r".encode())
        self._ser.write(f"diameter {syringe_diameter_mm}\r".encode())

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.rate = _ureg.parse_expression("0 mL/min")
        self._ser.write(b"stop\r")

        del self._ser

    async def _update(self):
        rate_mlmin = self.rate.to(_ureg.ml / _ureg.min).magnitude
        if rate_mlmin == 0:
            self._ser.write(b"stop\r")
        else:
            self._ser.write(f"irate {rate_mlmin} m/m\r".encode())
            self._ser.write(b"irun\r")
