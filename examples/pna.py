import mechwolf as mw
from datetime import timedelta

# define vessels
hatu = mw.Vessel("HATU", name="hatu")
dmf = mw.Vessel("DMF", name="dmf")
output = mw.Vessel("waste", name="output")
diea = mw.Vessel("DIEA", name = "diea")
pip = mw.Vessel("40% Piperidine in DMF", name = "pip")

# define pumps
coupling_pump = mw.VarianPump(name="coupling_pump")
amino_pump = mw.VarianPump(name="amino_pump")
diea_pump = mw.VarianPump(name="diea_pump")

mixer = mw.TMixer(name='mixer')

# define amines
fmoc_pna_a = mw.Vessel("fmoc_pna_a", name="fmoc_pna_a")
fmoc_pna_t = mw.Vessel("fmoc_pna_t", name="fmoc_pna_t")
fmoc_pna_c = mw.Vessel("fmoc_pna_c", name="fmoc_pna_c")
fmoc_pna_g = mw.Vessel("fmoc_pna_g", name="fmoc_pna_g")
fmoc_lys_oh = mw.Vessel("fmoc_lys_oh", name="fmoc_lys_oh")

# dummy passive heater
# heater = mw.Component("heater")

# define valve
amino_mapping = dict(fmoc_pna_a = 1,
                     fmoc_pna_t = 2,
                     fmoc_pna_c = 3,
                     fmoc_pna_g = 4,
                     fmoc_lys_oh = 5,
                     dmf = 10)

amino_valve = mw.ViciValve(name = "amino_valve", mapping = amino_mapping)

act_mapping = dict(hatu = 1,
                   pip = 9,
                   dmf  = 10)

coupling_valve = mw.ViciValve(name = "coupling_valve", mapping = act_mapping)

fat_tube = mw.Tube(length="2 foot", ID="1/16 in", OD="1/8 in", material="PFA")
thin_tube = mw.Tube(length="2 foot", ID="0.04 in", OD="1/16 in", material="PFA")
valve_tube = mw.Tube(length="43.3 cm", ID="0.030 in", OD="1/16 in", material="PFA")

A = mw.Apparatus("Automated Fast Flow Peptoid Synthesizer")

A.add(hatu, coupling_valve, mw.Tube(length="130 cm", ID="1/16 in", OD="1/8 in", material="PFA"))
A.add([dmf, pip], coupling_valve, fat_tube)
A.add(coupling_valve, coupling_pump, valve_tube)
A.add(coupling_pump, mixer, thin_tube)
A.add([fmoc_pna_a, fmoc_pna_t, fmoc_pna_c, fmoc_pna_g, fmoc_lys_oh, dmf], amino_valve, fat_tube)
A.add(amino_valve, amino_pump, valve_tube)
A.add(amino_pump, mixer, thin_tube)
A.add(diea, diea_pump, fat_tube)
A.add(diea_pump, mixer, thin_tube)
# A.add(mixer, heater, thin_tube)
# A.add(heater, output, thin_tube)

# A.describe()
A.visualize(graph_attr=dict(splines="ortho", nodesep="0.75"), label_tubes=False)

P = mw.Protocol(A, duration="auto")
start = timedelta(seconds=0)

# how much time to leave the pumps off before and after switching the valve
switching_time = timedelta(seconds=1)

pna = ['fmoc_pna_a', 'fmoc_pna_t', 'fmoc_pna_c', 'fmoc_pna_g']

def add_rinse():
    global start
    rinse_duration = timedelta(minutes=2)
    P.add([amino_valve, coupling_valve], start=start, duration=rinse_duration, setting="dmf")
    P.add([amino_pump, coupling_pump], start=start+switching_time, duration=rinse_duration - 2*switching_time, rate="5 mL/min")
    start += rinse_duration


def add_diea_rinse():
    # Washes with all three pumps while coupling agent and amino acid flushes out
    global start
    rinse_duration = timedelta(minutes=2)
    P.add([amino_valve, coupling_valve], start=start, duration=rinse_duration, setting="dmf")
    P.add([amino_pump, coupling_pump, diea_pump], start=start+switching_time, duration=rinse_duration - 2*switching_time, rate="5 mL/min")
    start += rinse_duration

for base in pna:
    add_rinse()

    # Turn on amino acid, coupling agent, and diea. does not implement about a priming period 
    coupling_duration = timedelta(minutes=1, seconds=30)

    P.add(amino_valve, start=start, duration=coupling_duration, setting=base)
    P.add(coupling_valve, start=start, duration=coupling_duration, setting="hatu")
    P.add([amino_pump, coupling_pump, diea_pump], start=start+switching_time, duration=coupling_duration - 2*switching_time, rate="5 mL/min")

    start += coupling_duration

    add_diea_rinse()
    add_rinse()

    # Fmoc removal
    pip_addition_duration = timedelta(minutes=1, seconds=30)

    P.add(amino_pump, start=start+switching_time, duration=pip_addition_duration - 2*switching_time, rate="5 mL/min")
    P.add(amino_valve, start=start, duration=pip_addition_duration, setting="dmf")
    P.add(coupling_valve, start=start, duration=pip_addition_duration, setting="dmf")

    start += pip_addition_duration

    add_rinse()

add_rinse()
add_rinse()

#print(P.yaml())
print(P.visualize())
#P.execute()
