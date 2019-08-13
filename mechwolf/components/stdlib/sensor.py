import asyncio
import time
from typing import TYPE_CHECKING, AsyncGenerator, Optional
from warnings import warn

from loguru import logger

from . import _ureg
from .active_component import ActiveComponent

if TYPE_CHECKING:
    import mechwolf


class Sensor(ActiveComponent):
    """
    A generic sensor.

    Attributes:
    - `name`: The name of the Sensor.
    - `rate`: Data collection rate in Hz as a `pint.Quantity`. A rate of 0 Hz corresponds to the sensor being off.
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name=name)
        self.rate = _ureg.parse_expression("0 Hz")
        self._visualization_shape = "ellipse"
        self._unit: str = ""
        self._base_state = {"rate": "0 Hz"}

    async def _read(self):
        """
        Collects the data.
        In the generic `Sensor` implementation, this raises a `NotImplementedError`.
        Subclasses of `Sensor` should implement their own version of this method.
        """
        raise NotImplementedError

    async def _monitor(
        self, experiment: "mechwolf.Experiment", dry_run: bool = False
    ) -> AsyncGenerator:
        """
        If data collection is off and needs to be turned on, turn it on.
        If data collection is on and needs to be turned off, turn off and return data.
        """
        while not experiment._end_loop:
            # if the sensor is off, hand control back over
            if not self.rate:
                await asyncio.sleep(0)
                continue

            if not dry_run:
                yield {"data": await self._read(), "timestamp": time.time()}
            else:
                yield {"data": "simulated read", "timestamp": time.time()}

            # then wait for the sensor's next read
            if self.rate:
                await asyncio.sleep(1 / self.rate.to_base_units().magnitude)

        logger.debug(f"Monitor loop for {self} has completed.")

    def _validate(self, dry_run: bool) -> None:
        logger.debug(f"Perfoming sensor specific checks for {self}...")
        if not dry_run:
            logger.trace(f"Executing Sensor-specific checks...")
            logger.trace("Entering context...")
            with self:
                logger.trace("Context entered")
                res = asyncio.run(self._read())
                if not res:
                    warn(
                        "Sensor reads should probably return data. "
                        f"Currently, {self}._read() does not return anything."
                    )
        logger.trace("Performing general component checks...")
        super()._validate(dry_run=dry_run)

    async def _update(self) -> None:
        # sensors don't have an update method; they implement read
        pass
