from components import Test
from connection import DeviceExecutor
import Pyro4

DEVICE_NAME = "valve1"

me = Test(name=DEVICE_NAME)
my_executor = DeviceExecutor(me)

with Pyro4.Daemon() as daemon:
    uri = daemon.register(my_executor)
    with Pyro4.locateNS() as ns:
        ns.register(DEVICE_NAME, uri)
        daemon.requestLoop()
