from .sensor import Sensor


class LabJack(Sensor):
    """
    A driver for the LabJack U3-LV data collection device.
    Currently set up to read differential input between FIO1 and FIO0.
    See labjack.com for more details on their python API.
    """

    def __init__(self, name=None):
        super().__init__(name=name)
        try:
            import u3  # noqa
        except ImportError:
            raise ImportError(
                "Unable to create LabJack."
                " No u3 module installed."
                " Try getting it here: https://github.com/labjack/LabJackPython/blob/master/src/u3.py."
            )

    def __enter__(self):
        self.device = u3.U3()  # noqa
        self.device.configIO(FIOAnalog=15)  # Configure FIO 0-3 as analog in
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # close the serial connection
        self.device.close()

    def read(self):
        return self.device.getAIN(0, 1)
