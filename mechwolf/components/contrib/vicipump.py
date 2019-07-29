from ..stdlib.pump import Pump
from . import ureg


class ViciPump(Pump):
    """A Vici M50 pump.
    This pump is characterized by the volume of fluid dispensed per revolution
    which can be found on the certificate of conformance
    This is specified in ml now, we can perhaps make it a ureg later
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

    def __init__(self, name, serial_port, volume_per_rev):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self.serial_port = serial_port
        self.volume_per_rev = ureg.parse_expression(volume_per_rev)

    def __enter__(self):
        import aioserial

        self.ser = aioserial.AioSerial(
            self.serial_port,
            9600,
            parity=aioserial.PARITY_NONE,
            stopbits=1,
            timeout=0.1,
            write_timeout=0.1 )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.rate = ureg.parse_expression("0 mL/min")
        self.ser.write(b'SL 0\r\n') # Stop pump
        del self.ser

    async def set_flow(self, flow_rate):

        steps_per_rev = 51200
        gear_ratio = 9.86

        steps_per_second = steps_per_rev / self.volume_per_rev.to(ureg.ml).magnitude
        steps_per_second *= flow_rate.to(ureg.ml / ureg.sec).magnitude
        steps_per_second *= gear_ratio
        steps_per_second = int(steps_per_second)

        flow_command = "SL {}\r\n".format(steps_per_second)

        await self.ser.write_async(flow_command.encode(encoding="ascii"))

        self.ser.reset_input_buffer()

    async def update(self):
        await self.set_flow(self.rate)
