from .component import ActiveComponent

class _Dummy(ActiveComponent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.active = False

    def base_state(self):
        return dict(active=False)

    def update(self):
        if self.active:
            print("Active!")
        else:
            print("Inactive.")
        return self.__dict__
