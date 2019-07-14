from typing import Optional

from . import ureg
from .active_component import ActiveComponent
from .tube import Tube


class TempControl(ActiveComponent):
    """
    A generic temperature controller.

    Attributes:
    - name (`str`): The name of the Sensor.
    - internal_tubing (`Tube`): The tubing inside the temperature controller.
    - temp (`pint.Quantity`): The temperature setting.
    - active (`bool`): Whether the temperature controller is active.
    """

    def __init__(self, internal_tubing: Tube, name: Optional[str] = None):
        super().__init__(name=name)
        if not isinstance(internal_tubing, Tube):
            raise TypeError("TempControl must have internal_tubing of type Tube.")
        self.temp = ureg.parse_expression("0 degC")
        self.active = False

    def base_state(self) -> dict:
        """
        Default to being inactive.
        """
        return dict(temp="0 degC", active=False)
