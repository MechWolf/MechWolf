from .component import ActiveComponent

class Valve(ActiveComponent):
    """A generic valve.

    Note:
        Users should not directly instantiate an :class:`Valve` for use in a :class:`~mechwolf.Protocol` becuase
        it is not an actual laboratory instrument.

    Attributes:
        name (str, optional): The name of the Valve.
        mapping (dict): The mapping from components to their integer port numbers.
        active (bool): Whether the temperature controller is active.
    """
    def __init__(self, mapping={}, name=None):
        super().__init__(name=name)
        self.mapping = mapping
        self.setting = 1

    def base_state(self):
        '''Default to the first mapping.

        This is an arbitrary choice but is guaranteed to be a valid setting.'''
        return dict(setting=list(self.mapping.items())[0][1])
