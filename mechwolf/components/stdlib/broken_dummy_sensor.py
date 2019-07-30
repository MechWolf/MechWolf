from typing import Optional

from .sensor import Sensor


class BrokenDummySensor(Sensor):
    """
    A dummy sensor returning the number of times it has been read. After a few reads, it fails, raising a `RuntimeError`.

    ::: danger
    Using this component during real protocol execution will result in a failure.
    :::

    Attributes:
    - `name` (str, optional): The name of the Sensor.
    - `rate` (Quantity): Data collection rate in Hz. A rate of 0 Hz corresponds to the sensor being off.
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name=name)
        self._unit = "Dimensionless"
        self.counter = 0

    async def read(self) -> int:
        """Collect the data."""
        self.counter += 1
        if self.counter > 15 and self.rate:
            raise RuntimeError("Unsurprisingly, the broken sensor is broken.")
        return self.counter
