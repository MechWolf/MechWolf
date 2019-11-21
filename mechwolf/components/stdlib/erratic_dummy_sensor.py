import random
from math import sin
from typing import Optional

from .sensor import Sensor


class ErraticDummySensor(Sensor):
    """A dummy sensor that sometimes fails and starts returning 0.

    ::: danger
    Don't use this in a real apparatus! It doesn't return real data.
    :::

    Attributes:
    - `name`: The component's name.
    - `rate`: Data collection rate in Hz as a `pint.Quanity`. A rate of 0 Hz corresponds to the sensor being off.
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name=name)
        self._unit = "Dimensionless"
        self._counter = 0.0
        self._fail_silently = False
        self._last_value = 0.0

    async def _read(self) -> float:
        """Collect the data."""
        if self._fail_silently:
            return 0
        self._fail_silently = (
            random.choices([True, False], weights=[1, 99])[0] and self._counter > 100
        )
        self._counter += 0.2
        return_value = sin(self._counter) + (((random.random() * 2) - 1) / 20) + 1
        self._last_value = return_value
        return return_value
