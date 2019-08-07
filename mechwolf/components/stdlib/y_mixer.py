from typing import Optional

from .mixer import Mixer


class YMixer(Mixer):
    """
    A Y mixer.

    This is an alias of `Component`.

    Arguments:
    - `name`: The name of the mixer.

    Attributes:
    - See arguments.
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name=name)
