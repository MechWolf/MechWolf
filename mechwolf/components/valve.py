from loguru import logger

from .component import ActiveComponent


class Valve(ActiveComponent):
    """A generic valve.

    Note:
        Users should not directly instantiate an :class:`Valve` for use in a :class:`~mechwolf.Protocol` becuase
        it is not an actual laboratory instrument.

    Attributes:
        mapping (dict): The mapping from components to their integer port numbers.
        name (str, optional): The name of the Valve.
        setting (int): The position of the valve.
    """

    def __init__(self, mapping, name=None):
        super().__init__(name=name)
        self.mapping = mapping
        self.setting = 1
        self._visualization_shape = "parallelogram"

    def base_state(self):
        """Default to the first setting.

        This is an arbitrary choice but is guaranteed to be a valid setting."""
        return {"setting": 1}


class DummyValve(Valve):
    def __init__(self, name=None, mapping={}):
        super().__init__(name=name, mapping=mapping)

    def update(self):
        logger.trace(f"Switching {self.name} to position {self.setting}")
        return True
