import mechwolf as mw

# define the vessels
vessel_1 = mw.Vessel("10 mL `4-aminophenol`")
vessel_2 = mw.Vessel("10 mL `acetic anhydride`")
vessel_3 = mw.Vessel("`acetaminophen`")

# define the pumps
pump_1 = mw.Pump(name="pump_1")
pump_2 = mw.Pump(name="pump_2")

# define the mixer
mixer = mw.TMixer()

# same tube specs for all tubes
tube = mw.Tube(
    length="1 m",
    ID="1/16 in",
    OD="2/16 in",
    material="PVC")

# create the Apparatus object
A = mw.Apparatus()

# add the connections
A.add(vessel_1, pump_1, tube)
A.add(vessel_2, pump_2, tube)
A.add(pump_1, mixer, tube)
A.add(pump_2, mixer, tube)
A.add(mixer, vessel_3, tube)

# visualize
A.summarize()
A.describe()
A.visualize(title=False)

# create the Protocol object
P = mw.Protocol(A, name="acetaminophen synthesis")
P.add([pump_1, pump_2], duration="10 mins", rate="1 mL/min")

# inspect the protocol
P.visualize()
print(P.yaml())
