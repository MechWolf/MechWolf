from typing import Optional

from . import ureg
from .active_component import ActiveComponent


class Pump(ActiveComponent):
    """
    A generic pumping device whose primary feature is that it moves fluid.

    Arguments:
    - `name`: The name of the pump.

    Attributes:
    - `name`: The name of the pump.
    - `rate`: The flow rate of the pump as a `pint.Quantity`. Must be of the dimensionality of volume/time.
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
