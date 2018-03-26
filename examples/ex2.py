from components import Pump, Tube, Vessel
from flow import Apparatus, Protocol

vessel_1 = Vessel("1 mL `EtOH` in 10 mL water", resolve=False)
pump_1 = Pump(name="pump_1")
vessel_2 = Vessel("`EtOH` in water in a 1:10 ratio", resolve=False)

tube = Tube(length="1 m",
            ID="1/16 in",
            OD="2/16 in",
            material="PVC")

# create the Apparatus object
A = Apparatus()

# add the connections
A.add(vessel_1, pump_1, tube)
A.add(pump_1, vessel_2, tube)

P = Protocol(A)
P.add(pump_1, rate="1 mL/min", duration="5 mins")
print(P.json())
