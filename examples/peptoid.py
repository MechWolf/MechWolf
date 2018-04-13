import mechwolf as mw

# define vessels
coupling_agent = mw.Vessel("HATU", name="coupling_agent")
acid = mw.Vessel("bromoacetic acid", name="acid")
solvent = mw.Vessel("solvent", name="solvent")
output = mw.Vessel("waste", name="output")

# define pumps
coupling_pump = mw.Pump(name="coupling_pump")
base_pump = mw.Pump(name="base_pump")
amine_pump = mw.Pump(name="amine_pump")
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

# define valve
mapping = dict(amine_1=1,
               amine_2=2,
               amine_3=3,
               amine_4=4,
               amine_5=5,
               amine_6=6,
               amine_7=7,
               amine_8=8,
               solvent=9,
               acid=10)
valve = mw.Valve(name="valve", mapping=mapping)


tube = mw.Tube(length="1 foot", ID="1/16 in", OD="1/8 in", material="PFA")

A = mw.Apparatus("Automated Fast Flow Peptoid Synthesizer")

A.add(coupling_agent, coupling_pump, tube)
A.add(coupling_pump, mixer, tube = mw.Tube(length="1 foot", ID="0.0030 in", OD="1/16 in", material="PFA"))
A.add([amine_1, amine_2, amine_3, amine_4, amine_5, amine_6, amine_7, amine_8, solvent, acid], valve, tube)
A.add(valve, amine_pump, tube)
A.add(amine_pump, mixer, tube = mw.Tube(length="1 foot", ID="0.0030 in", OD="1/16 in", material="PFA"))
A.add(mixer, output, tube = mw.Tube(length="1 foot", ID="0.0030 in", OD="1/16 in", material="PFA"))

A.summarize()
A.visualize(graph_attr=dict(splines="ortho", nodesep="0.5"))
