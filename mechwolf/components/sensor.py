from .component import ActiveComponent
import asyncio

class Sensor(ActiveComponent):
    """A generic sensor.

    Note:
        Users should not directly instantiate an :class:`Sensor` for use in a :class:`~mechwolf.Protocol` becuase
        it is not an actual laboratory instrument.

    Attributes:
        name (str, optional): The name of the Sensor.
        active (bool): Whether the sensor is active.
        interval (int): Data collection interval, in seconds. Default is 1 sec. 
    """

    def __init__(self, name, interval=1):
        super().__init__(name=name)
        self.active = False
        self.interval = interval

    def base_state(self):
        '''Default to being inactive.'''
        return dict(active=False)

    def read_sensor(self):
        '''Return data to be sent back to the hub.'''
        #Do data collection task here
        data = 2
        return data

    def config(self):
        '''Default to one second interval'''
        return {"interval": (int, 1)}

    async def update(self):
        '''If data collection is off and needs to be turned on, turn it on.
           If data collection is on and needs to be turned off, turn off and return data.'''
        while self.active:
            yield self.read_sensor()
            await asyncio.sleep(self.interval)
        
