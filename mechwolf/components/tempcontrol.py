from . import term, ureg
from .component import ActiveComponent
from .tube import Tube


class TempControl(ActiveComponent):
    """A generic temperature controller.

    Note:
        Users should not directly instantiate an :class:`TempControl` for use in a :class:`~mechwolf.Protocol` becuase
        it is not an actual laboratory instrument.

    Attributes:
        name (str, optional): The name of the Sensor.
        internal_tubing (Tube): The tubing inside the temperature controller.
        temp (str): The temperature setting. Converted to a Quantity.
        active (bool): Whether the temperature controller is active.
    """

    def __init__(self, name, internal_tubing):
        super().__init__(name=name)
        if not isinstance(internal_tubing, Tube):
            raise TypeError(term.red("TempControl must have internal_tubing of type Tube."))
        self.temp = ureg.parse_expression("0 degC")
        self.active = False

    def base_state(self):
        '''Default to being inactive.'''
        return dict(temp="0 degC", active=False)
