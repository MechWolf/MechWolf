from components import Test, Vessel, Tube
from connection import DeviceExecutor
from flow import Apparatus, Protocol

import sys
import Pyro4
import Pyro4.util

sys.excepthook = Pyro4.util.excepthook

input_vessel = Vessel("`glucose`, `indium(iii) bromide`, and `triflic acid` in a 50/50 mix of `chloroform` and `acetonitrile`", resolve=False, warnings=False)
test = Test(name="valve1")
output_vessel = Vessel("the output of the reaction")

A = Apparatus()
A.add(input_vessel, test, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))
A.add(test, output_vessel, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))

P = Protocol(A, duration="auto")
P.add(test, active=True, duration="5 secs")
P.add(test, active=False, start_time="5 secs", duration="1 sec")
P.add(test, active=True, start_time="6 secs", duration="2 sec")

P.execute()