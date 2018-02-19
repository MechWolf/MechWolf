from components import Valve
from connection import DeviceExecutor

import sys
import Pyro4
import Pyro4.util

sys.excepthook = Pyro4.util.excepthook


with Valve('/dev/tty.usbserial') as v:
    e = Pyro4.Proxy("PYRONAME:de")
    for i in range(100):
        e.submit(v, i, v.set_position, (i%9)+1)
    e.submit(v, 4.5, v.set_position, 8)
    print (e._task_queue)
    e.run()