from .component import ActiveComponent
from . import ureg
import asyncio
import time

class Sensor(ActiveComponent):
    """A generic sensor.

    Note:
        Users should not directly instantiate an :class:`Sensor` for use in a :class:`~mechwolf.Protocol` becuase
        it is not an actual laboratory instrument.

    Attributes:
        name (str, optional): The name of the Sensor.
        rate (Quantity): Data collection rate in Hz. A rate of 0 Hz corresponds to the sensor being off.
    """

    def __init__(self, name):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 Hz")
        self._visualization_shape = "ellipse"
        self.done = False

    def base_state(self):
        '''Default to being inactive.'''
        return dict(rate="0 Hz")

    def read(self):
        '''Collect the data.'''
        raise NotImplementedError

    def update(self):
        return { "timestamp": time.time(),
                "params": {"rate": str(self.rate.to_base_units())},
                "device": self.name}

    async def monitor(self):
        '''If data collection is off and needs to be turned on, turn it on.
           If data collection is on and needs to be turned off, turn off and return data.'''
        while True:
            if self.done:
                print(f'Done monitoring {self.name}')
                break
            frequency = self.rate.to_base_units().magnitude
            if frequency != 0:
                yield { 'datapoint': self.read(),
                        'timestamp': time.time()}
                await asyncio.sleep(1/frequency)
            else:
                await asyncio.sleep(frequency)


class DummySensor(Sensor):
    """A dummy sensor returning the number of times it has been read.

    Warning:
        Don't use this in a real apparatus! It doesn't return real data.

    Attributes:
        name (str, optional): The name of the Sensor.
        rate (Quantity): Data collection rate in Hz. A rate of 0 Hz corresponds to the sensor being off.
    """

    def __init__(self, name):
        super().__init__(name=name)
        self.counter = 0

    def read(self):
        '''Collect the data.'''
        self.counter += 1
        return self.counter
