from .component import ActiveComponent

class Sensor(ActiveComponent):
    """A generic sensor.

    Note:
        Users should not directly instantiate an :class:`Sensor` for use in a :class:`~mechwolf.Protocol` becuase
        it is not an actual laboratory instrument.

    Attributes:
        name (str, optional): The name of the Sensor.
        active (bool): Whether the sensor is active.
    """
    def __init__(self, name):
        super().__init__(name=name)
        self.active = False

    def base_state(self):
        '''Default to being inactive.'''
        return dict(active=False)
