from flow import Apparatus, Protocol
from components import Tube, Vessel, Test

input_vessel = Vessel("`glucose`, `indium(iii) bromide`, and `triflic acid` in a 50/50 mix of `chloroform` and `acetonitrile`", warnings=False)
test = Test("test_1")

A = Apparatus()
A.add(input_vessel, test, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))

P = Protocol(A)
P.add(test, active=True, start_time="3 secs", stop_time="5 seconds")

P.execute("http://127.0.0.1:5000/submit_protcol")