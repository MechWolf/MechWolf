import mechwolf as mw

vessel_1 = mw.Vessel("1 mL `EtOH` in 10 mL water", resolve=False)
pump_1 = mw.Pump(name="pump_1")
vessel_2 = mw.Vessel("`EtOH` in water in a 1:10 ratio", resolve=False)

tube = mw.Tube(
    length="1 m",
    ID="1/16 in",
    OD="2/16 in",
    material="PVC")

# create the Apparatus object
A = mw.Apparatus()

# add the connections
A.add(vessel_1, pump_1, tube)
A.add(pump_1, vessel_2, tube)
# print(A.summarize())
P = mw.Protocol(A)
P.add(pump_1, rate="1 mL/min", duration="5 mins")
P.visualize()
# print(P.json())
