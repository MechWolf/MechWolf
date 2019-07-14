from .mixer import Mixer


class TMixer(Mixer):
    """
    A T mixer.

    This is an alias of `Component`.

    Attributes:
    - `name` (`str`, optional): The name of the mixer.
    """

    def __init__(self, name=None):
        super().__init__(name=name)
