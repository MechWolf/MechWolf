from .component import Component

class TMixer(Component):
    """A T mixer.

    This is an alias of :class:`~mechwolf.Component`.

    Attributes:
        name (str, optional): The name of the mixer.
    """
    def __init__(self, name=None):
        super().__init__(name=name)

class YMixer(Component):
    """A Y mixer.

    This is an alias of :class:`~mechwolf.Component`.

    Attributes:
        name (str, optional): The name of the mixer.
    """

    def __init__(self, name=None):
        super().__init__(name=name)
