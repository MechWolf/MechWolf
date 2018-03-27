from .pump import Pump

class VarianPump(Pump):
    '''A Varian pump.
    '''
    def __init__(self, name=None, max_rate=0):
        super().__init__(name=name)
        self.rate = "0 ml/min"
        self.max_rate = max_rate

    def base_state(self):
        '''Returns the base state of a pump'''
        return dict(rate="0 ml/min")

    def update(self):
        print(ureg.parse_expression(self.rate).to(ureg.ml / ureg.min).magnitude / self.max_rate)
