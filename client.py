from components import Test
import requests
import json

# from connection import DeviceExecutor
# import Pyro4

DEVICE_NAME = "heater"

me = Test(name=DEVICE_NAME)
# my_executor = DeviceExecutor(me)

# with Pyro4.Daemon() as daemon:
#     uri = daemon.register(my_executor)
#     with Pyro4.locateNS() as ns:
#         ns.register(DEVICE_NAME, uri)
#         daemon.requestLoop()

# from socketIO_client import SocketIO

# with SocketIO('localhost:5000') as socketIO:
# 	for i in range(10):
# 	    socketIO.emit("message", dict(count=i))
# 	    socketIO.wait(seconds=1)

print(requests.post("http://127.0.0.1:5000/protocol", data=dict(device_id=DEVICE_NAME)).text)


