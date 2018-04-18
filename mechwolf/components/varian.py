from .pump import Pump
from . import ureg

class VarianPump(Pump):
    '''A Varian pump.
    '''
    def __init__(self, name=None, max_rate=0):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self.max_rate = max_rate

    def update(self):
        print(ureg.parse_expression(self.rate).to(ureg.ml / ureg.min).magnitude / self.max_rate)

    def config(self):
        return dict(max_rate=(int, None))
