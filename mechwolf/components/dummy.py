from .component import ActiveComponent

class Dummy(ActiveComponent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.active = False

    def base_state(self):
        return dict(active=False)

    async def update(self):
        if self.active:
            print("Active and async!")
        else:
            print("Inactive and async.")
        yield self.__dict__

    def config(self):
        return {}
