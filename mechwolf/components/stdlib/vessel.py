from .component import Component


class Vessel(Component):
    """A generic vessel.

    Attributes:
        description (str): The contents of the vessel.
        name (str): The name of the vessel, if different from the description.
    """  # noqa

    def __init__(self, description, name=None):
        super().__init__(name=name)
        self.description = description
        self._visualization_shape = "cylinder"
