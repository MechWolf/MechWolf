from .component import ActiveComponent

class Valve(ActiveComponent):
    def __init__(self, mapping={}, name=None):
        super().__init__(name=name)
        self.mapping = mapping
        self.setting = 1

    def base_state(self):
        # an arbitrary state
        return dict(setting=list(self.mapping.items())[0][1])

    def update(self):
        print(f"Setting at {self.setting}")
