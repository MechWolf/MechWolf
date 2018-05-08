import mechwolf as mw
from datetime import timedelta

# define vessels
coupling_agent = mw.Vessel("HATU", name="coupling_agent")
acid = mw.Vessel("bromoacetic acid", name="acid")
solvent = mw.Vessel("solvent", name="solvent")
output = mw.Vessel("waste", name="output")

# define pumps
coupling_pump = mw.VarianPump(name="pump_3")
amine_pump = mw.VarianPump(name="pump_2")
mixer = mw.TMixer()

# define amines
amine_1 = mw.Vessel("amine_1", name="amine_1")
amine_2 = mw.Vessel("amine_2", name="amine_2")
amine_3 = mw.Vessel("amine_3", name="amine_3")
amine_4 = mw.Vessel("amine_4", name="amine_4")
amine_5 = mw.Vessel("amine_5", name="amine_5")
amine_6 = mw.Vessel("amine_6", name="amine_6")
amine_7 = mw.Vessel("amine_7", name="amine_7")
amine_8 = mw.Vessel("amine_8", name="amine_8")

# dummy passive heater
# heater = mw.Component("heater")

# define valve
amine_mapping = dict(amine_1 = 1,
                     amine_2 = 2,
                     amine_3 = 3,
                     amine_4 = 4,
                     amine_5 = 5,
                     amine_6 = 6,
                     amine_7 = 7,
                     amine_8 = 8,
                     acid    = 9,
                     solvent = 10)
valve = mw.ViciValve(name = "valve", mapping = amine_mapping)

act_mapping = dict(coupling_agent = 1,
                   solvent        = 2)

coupling_valve = mw.ViciValve(name = "coupling_valve", mapping = act_mapping)

fat_tube = mw.Tube(length="2 foot", ID="1/16 in", OD="1/8 in", material="PFA")
thin_tube = mw.Tube(length="2 foot", ID="0.04 in", OD="1/16 in", material="PFA")

A = mw.Apparatus("Automated Fast Flow Peptoid Synthesizer")

A.add(coupling_agent, coupling_valve, mw.Tube(length="130 cm", ID="1/16 in", OD="1/8 in", material="PFA"))
A.add(solvent, coupling_valve, fat_tube)
A.add(coupling_valve, coupling_pump, fat_tube)
A.add(coupling_pump, mixer, thin_tube)
A.add([amine_1, amine_2, amine_3, amine_4, amine_5, amine_6, amine_7, amine_8, solvent, acid], valve, fat_tube)
A.add(valve, amine_pump, fat_tube)
A.add(amine_pump, mixer, thin_tube)
# A.add(mixer, heater, thin_tube)
# A.add(heater, output, thin_tube)

# A.describe()
A.visualize(graph_attr=dict(splines="ortho", nodesep="0.75"), label_tubes=False)

P = mw.Protocol(A, duration="auto")
start = timedelta(seconds=0)

# how much time to leave the pumps off before and after switching the valve
switching_time = timedelta(seconds=1)

def add_rinse():
    global start
    rinse_duration = timedelta(minutes=2)
    P.add([valve, coupling_valve], start=start, duration=rinse_duration, setting="solvent")
    P.add([amine_pump, coupling_pump], start=start+switching_time, duration=rinse_duration - 2*switching_time, rate="5 mL/min")
    start += rinse_duration

peptoid = ["amine_2", "amine_2", "amine_1", "amine_2"]

for amine in peptoid:
    add_rinse()

    # acid coupling
    coupling_duration = timedelta(minutes=1, seconds=30)
    P.add(valve, start=start, duration=coupling_duration, setting="acid")
    P.add(coupling_valve, start=start, duration=coupling_duration, setting="coupling_agent")
    
    P.add([amine_pump, coupling_pump], start=start+switching_time, duration=coupling_duration - 2*switching_time, rate="5 mL/min")
    start += coupling_duration

    add_rinse()

    # amine addition
    amine_addition_duration = timedelta(minutes=1, seconds=30)
    P.add(amine_pump, start=start+switching_time, duration=amine_addition_duration - 2*switching_time, rate="5 mL/min")
    P.add(valve, start=start, duration=amine_addition_duration, setting=amine)
    start += amine_addition_duration

add_rinse()
add_rinse()

#print(P.yaml())
print(P.visualize())
#P.execute()
