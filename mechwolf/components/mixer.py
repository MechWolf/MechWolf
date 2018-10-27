from .component import Component

class Mixer(Component):
    """A generic mixer.

    This is an alias of :class:`~mechwolf.Component`.

    Attributes:
        name (str, optional): The name of the mixer.
    """

    def __init__(self, name=None):
        super().__init__(name=name)
        self._visualization_shape = "cds"

class TMixer(Mixer):
    """A T mixer.

    This is an alias of :class:`~mechwolf.Component`.

    Attributes:
        name (str, optional): The name of the mixer.
    """

    def __init__(self, name=None):
        super().__init__(name=name)

class YMixer(Mixer):
    """A Y mixer.

    This is an alias of :class:`~mechwolf.Component`.

    Attributes:
        name (str, optional): The name of the mixer.
    """

    def __init__(self, name=None):
        super().__init__(name=name)

class CrossMixer(Mixer):
    """A cross mixer.

    This is an alias of :class:`~mechwolf.Component`.

    Attributes:
        name (str, optional): The name of the mixer.
    """

    def __init__(self, name=None):
        super().__init__(name=name)
