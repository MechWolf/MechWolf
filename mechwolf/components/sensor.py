from .component import ActiveComponent

class Sensor(ActiveComponent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.active = False

    def base_state(self):
        return dict(active=False)
