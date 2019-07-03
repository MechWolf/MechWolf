import asyncio
import random
import time
from warnings import warn

from loguru import logger

from . import ureg
from .component import ActiveComponent


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
        self._unit = ""
        self._done = False

    def base_state(self):
        """Default to being inactive."""
        return dict(rate="0 Hz")

    def read(self):
        """Collect the data."""
        raise NotImplementedError

    async def monitor(self, dry_run=False):
        """If data collection is off and needs to be turned on, turn it on.
           If data collection is on and needs to be turned off, turn off and return data."""
        while True:

            if self._done:
                logger.trace(f"Done monitoring {self}")
                break
            elif not self.rate:
                await asyncio.sleep(0.1)  # try again in 100 ms
            else:
                if not dry_run:
                    yield {"data": self.read(), "timestamp": time.time()}
                else:
                    yield {"data": "simulated read", "timestamp": time.time()}
                await asyncio.sleep(1 / self.rate.to_base_units().magnitude)

    def validate(self, dry_run):
        logger.debug(f"Perfoming sensor specific checks for {self}...")
        if not dry_run:
            logger.trace(f"Executing Sensor-specific checks...")
            try:
                logger.trace("Entering context...")
                with self:
                    logger.trace("Context entered")
                    res = self.read()
                    logger.trace("Read successful")
            except NotImplementedError:
                warn("Sensors must have a read method that returns the sensor's data")
                return False

            if not res:
                warn(
                    "Sensor reads should probably return data. "
                    f"Currently, {self}.read() does not return anything."
                )
        logger.trace("Performing general component checks...")
        return super().validate(dry_run=dry_run)


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
        self._unit = "Dimensionless"
        self.counter = 0

    def read(self):
        """Collect the data."""
        self.counter += (random.random() * 2) - 1
        return self.counter

    def update(self):
        return True
