from typing import Optional

from .component import Component


class Vessel(Component):
    """
    A generic vessel.

    Arguments:
    - `description`: The contents of the vessel.
    - `name`: The name of the vessel, if different from the description.

    Attributes:
    - `description`: The contents of the vessel.
    - `name`: The name of the vessel, if different from the description.
    """

    def __init__(self, description: Optional[str] = None, name=None):
        super().__init__(name=name)
        self.description = description
        self._visualization_shape = "cylinder"
