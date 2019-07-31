from ..stdlib.sensor import Sensor


class LabJack(Sensor):
    """
    A driver for the LabJack U3-LV data collection device.
    Currently set up to read differential input between FIO1 and FIO0.
    See labjack.com for more details on their python API.
    """

    metadata = {
        "author": [
            {
                "first_name": "Alex",
                "last_name": "Mijalis",
                "email": "Alex Mijalis <Alexander_Mijalis@hms.harvard.edu>",
                "institution": "Harvard Medical School",
                "github_username": "amijalis",
            }
        ],
        "stability": "beta",
        "supported": True,
    }

    def __init__(self, name=None):
        super().__init__(name=name)

    def __enter__(self):
        try:
            import u3  # noqa

            self.device = u3.U3()  # noqa
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "No u3 module installed. "
                "Try using this command: "
                "pip install git+https://github.com/labjack/LabJackPython.git"
            )

        self.device.configIO(FIOAnalog=15)  # Configure FIO 0-3 as analog in
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # close the serial connection
        self.device.close()

    async def _read(self):
        return self.device.getAIN(0, 1)
