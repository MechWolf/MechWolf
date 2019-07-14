from typing import Optional

from . import ureg
from .component import ActiveComponent


class Pump(ActiveComponent):
    """
    A generic pumping device whose primary feature is that it moves fluid.

    Attributes:
    - `name` (`str`): The name of the pump.
    - `rate` (`pint.Quantity`): The flow rate of the pump. Must be of the dimensionality of volume/time.
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self._visualization_shape = "box3d"

    def base_state(self) -> dict:
        """
        A pump's base state is a flow rate of 0 mL/min.
        """
        return dict(rate="0 mL/min")


class DummyPump(Pump):
    """
    A fake pumping device whose primary feature is that it moves fluid, used internally for testing.

    ::: warning
    Users should not instantiate a `DummyPump` for use in a `Protocol` because it is not an actual laboratory instrument.
    :::

    Attributes:
    - `name` (`str`): The name of the pump.
    - `rate` (`pint.Quantity`): The flow rate of the pump. Must be of the dimensionality of volume/time.
    """

    def __init__(self, name=None):
        super().__init__(name=name)

    def update(self):
        return True
