from .component import ActiveComponent
from . import ureg

class Pump(ActiveComponent):
    '''A pumping device whose primary attribute is that it moves fluid.

    Note:
        Users should not directly instantiate an :class:`Pump` for use in a :class:`flow.Protocol` becuase
        it is not a functioning laboratory instrument

    Attributes:
        rate (str)
    '''
    def __init__(self, name=None):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")

    def base_state(self):
        '''Returns the base state of a pump'''
        return dict(rate="0 ml/min")
