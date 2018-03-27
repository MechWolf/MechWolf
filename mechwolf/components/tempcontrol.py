from colorama import Fore
from .component import ActiveComponent
from .tube import Tube

class TempControl(ActiveComponent):
    def __init__(self, internal_tubing, name=None):
        super().__init__(name=name)
        if type(internal_tubing) != Tube:
            raise TypeError(Fore.RED + "TempControl must have internal_tubing of type Tube.")
        self.temp = "0 degC"
        self.active = False

    def base_state(self):
        return dict(temp="0 degC", active=False)
