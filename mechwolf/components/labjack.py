from .sensor import Sensor
import u3

class LabJack(Sensor):
    """
    A driver for the LabJack U3-LV data collection device.
    Currently set up to read differential input between FIO1 and FIO0.
    See labjack.com for more details on their python API.
    """

    def __init__(self,name):
        super().__init__(name=name)

    def __enter__(self):
        self.device = u3.U3()
        self.device.configIO(FIOAnalog=15) #Configure FIO 0-3 as analog in
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # close the serial connection
        self.device.close()

    def read(self):
        return self.device.getAIN(0,1)
