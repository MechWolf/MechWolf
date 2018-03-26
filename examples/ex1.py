from mechwolf.components import VarianPump, TempControl, Tube, Vessel, Component
from mechwolf import Apparatus, Protocol

start_materials = Vessel("`start` material", name="start_materials")
pump_3 = VarianPump(name="pump_3")
oil_bath = Component('oil bath with tube (describe the tube)')
product = Vessel("", name="product")

A = Apparatus()
A.add(start_materials, pump_3, Tube("2 ft", "1/32 in", "1/16 in", "material"))
A.add(pump_3, oil_bath, Tube("20 ft", "1/16 in", "1/8 in", "material"))
A.add(oil_bath, product, Tube("2 ft", "1/32 in", "1/16 in", "material"))

P = Protocol(A, duration="auto")
P.add(pump_3, stop="1 second", rate="1 ml/min")

# P.execute()
