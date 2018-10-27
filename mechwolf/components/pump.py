from .component import ActiveComponent
from . import ureg

class Pump(ActiveComponent):
    '''A generic pumping device whose primary feature is that it moves fluid.

    Note:
        Users should not directly instantiate an :class:`Pump` for use in a :class:`~mechwolf.Protocol` becuase
        it is not an actual laboratory instrument.

    Attributes:
        name (str, optional): The name of the pump.
        rate (str): The flow rate of the pump. Must be of the dimensionality of volume/time. Converted to a Quantity.
    '''

    def __init__(self, name):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self._visualization_shape = "box3d"

    def base_state(self):
        '''Default to 0 mL/min.'''
        return dict(rate="0 mL/min")
