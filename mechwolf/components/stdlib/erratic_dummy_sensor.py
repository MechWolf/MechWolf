import random
from math import sin
from typing import Optional

from loguru import logger

from .sensor import Sensor


class ErraticDummySensor(Sensor):
    """A dummy sensor that fails in a variety of interesting ways.

    ::: danger
    Don't use this in a real apparatus! It doesn't return real data.
    :::

    Arguments:
    - `failure_mechanism`: One of "speed up", "slow down", "output same", "output zero", or "change amp"
    - `name`: The component's name.
    - `invocation_threshold`: The minimum number of reads before failure.

    Attributes:
    - `name`: The component's name.
    - `rate`: Data collection rate in Hz as a `pint.Quantity`. A rate of 0 Hz corresponds to the sensor being off.
    """

    def __init__(
        self, failure_mechanism, name: Optional[str] = None, invocation_threshold=100
    ):
        super().__init__(name=name)
        self._unit = "Dimensionless"
        self._failure_mechanism = failure_mechanism
        self._fail = False
        self._invocations = 0
        self._invocation_threshold = invocation_threshold
        self._value = 0.0
        self._last_value = 0.0
        self._inc = 0.1
        self._amp = 2.0

    async def _read(self) -> float:
        """Collect the data."""
        if self._invocations > self._invocation_threshold and not self._fail:
            self._fail = random.choices(
                [False, self._failure_mechanism], weights=[0, 1]
            )[0]

            # if the failure is new, emit a warning and change some params
            if self._fail == "speed up":
                self._inc = 2.5 * self._inc
                logger.warning(
                    f"{self} has encountered an anomaly and sped up at invocation #{self._invocations}"
                )
            elif self._fail == "slow down":
                self._inc = self._inc / 2
                logger.warning(
                    f"{self} has encountered an anomaly and slowed down at invocation #{self._invocations}"
                )
            elif self._fail == "output same":
                logger.warning(
                    f"{self} has encountered an anomaly and started outputting the same data at invocation #{self._invocations}"
                )
            elif self._fail == "output zero":
                logger.warning(
                    f"{self} has encountered an anomaly and started outputting zero at invocation #{self._invocations}"
                )
            elif self._fail == "change amp":
                self._amp = 3.0
                logger.warning(
                    f"{self} has encountered an anomaly and changed amplitude at invocation #{self._invocations}"
                )

        if self._fail == "output same":
            return_value = self._last_value
        elif self._fail == "output zero":
            return_value = 0
        else:
            self._value += self._inc
            return_value = (sin(self._value) + 1) / self._amp  # read from the sensor
            return_value += (random.random() - 0.5) / 5  # insert noise

            self._last_value = return_value

        self._invocations += 1
        return return_value
