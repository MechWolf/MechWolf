from .component import Component


class Mixer(Component):
    """
    A generic mixer.

    This is an alias of `Component`.

    Arguments:
    - `name`: The name of the mixer.

    Attributes:
    - `name`: The name of the mixer.
    """

    def __init__(self, name=None):
        super().__init__(name=name)
        self._visualization_shape = "cds"
