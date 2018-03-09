from flow import Apparatus, Protocol
from components import Tube, Vessel, Valve, Component, Test

a = Component(name="a")
b = Component(name="b")
c = Component(name="c")
# input_vessel = Vessel("`glucose`, `indium(iii) bromide`, and `triflic acid` in a 50/50 mix of `chloroform` and `acetonitrile`", resolve=False)
test = Valve(name="test_1", mapping=dict(a=1, b=2, c=3))
# test2 = Valve(name="test_2", mapping=dict(a=1, b=2, c=3))

A = Apparatus()
A.add(a, test, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))
A.add(b, test, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))
A.add(c, test, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))
# A.add(test, test2, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))


P = Protocol(A, duration="auto")
P.add(test, setting="a", start="3 secs", stop="4 secs")
P.add(test, setting="b", start="4 secs", stop="5 secs")
P.add(test, setting="c", start="5 secs", stop="6 secs")
# P.add(test2, active=True)
P.execute("http://127.0.0.1:5000/submit_protocol")
# print(P.compile())