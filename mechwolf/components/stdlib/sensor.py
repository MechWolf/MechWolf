import asyncio
import time
from typing import Any, AsyncGenerator, Dict, Optional
from warnings import warn

from loguru import logger

from . import ureg
from .active_component import ActiveComponent

from IPython import get_ipython

class Sensor(ActiveComponent):
    """
    A generic sensor.

    Attributes:
    - `name`: The name of the Sensor.
    - `rate`: Data collection rate in Hz as a `pint.Quantity`. A rate of 0 Hz corresponds to the sensor being off.
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 Hz")
        self._visualization_shape = "ellipse"
        self._unit = ""
        self._stop = False

    def base_state(self) -> Dict[str, Any]:
        """
        Default to being inactive.
        """
        return dict(rate="0 Hz")

    async def read(self):
        """
        Collects the data.
        In the generic `Sensor` implementation, this raises a `NotImplementedError`.
        Subclasses of `Sensor` should implement their own version of this method.
        """
        raise NotImplementedError

    async def monitor(self, dry_run: bool = False) -> AsyncGenerator:
        """
        If data collection is off and needs to be turned on, turn it on.
        If data collection is on and needs to be turned off, turn off and return data.
        """
        while True:

            if self._stop:
                logger.trace(f"Done monitoring {self}")
                break
            elif not self.rate:
                await asyncio.sleep(0.1)  # try again in 100 ms
            else:
                if not dry_run:
                    yield {"data": await self.read(), "timestamp": time.time()}
                else:
                    yield {"data": "simulated read", "timestamp": time.time()}
                await asyncio.sleep(1 / self.rate.to_base_units().magnitude)

    def validate(self, dry_run: bool) -> None:
        logger.debug(f"Perfoming sensor specific checks for {self}...")
        if not dry_run:
            logger.trace(f"Executing Sensor-specific checks...")
            logger.trace("Entering context...")
            with self:
                logger.trace("Context entered")
    #            res = task.result()
    #        if not res:
    #            warn(
    #                "Sensor reads should probably return data. "
    #                f"Currently, {self}.read() does not return anything."
    #            )
        logger.trace("Performing general component checks...")
        super().validate(dry_run=dry_run)

    def update(self) -> None:
        # sensors don't have an update method; they implement read
        pass
