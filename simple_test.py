from flow import Apparatus, Protocol
from components import Component, Tube, Pump, Sensor, Valve, TempControl, Vessel

input_vessel = Vessel("`glucose`, `indium(iii) bromide`, and `triflic acid` in a 50/50 mix of `chloroform` and `acetonitrile`", warnings=False)
pump = Pump("pump1")
heater = Component(name="heater")
output_vessel = Vessel("the output of the reaction")

A = Apparatus()
A.add(input_vessel, pump, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))
A.add(pump, heater, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))
A.add(heater, output_vessel, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))

P = Protocol(A)
P.add(pump, rate="15 ml/min", duration="1 min")