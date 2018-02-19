from components import ViciValve
from connection import DeviceExecutor
import Pyro4

DEVICE_NAME = "valve1"

my_executor = DeviceExecutor()

# for example purposes we will access the daemon and name server ourselves and not use serveSimple
with Pyro4.Daemon() as daemon:
    my_uri = daemon.register(my_executor)
    with Pyro4.locateNS() as ns:
        ns.register("de", my_uri)
    daemon.requestLoop()
