from datetime import timedelta, datetime

import mechwolf as mw

#define the components
alanine = mw.Vessel("15 ml `fmoc-L-Alanine` in 10 g of `salt`", resolve=False)
cysteine = mw.Vessel("20 ml `water`", resolve=False)
alanine_pump = mw.Pump(name="alanine_pump")
cysteine_pump = mw.Pump(name="cysteine_pump")

valve = mw.Valve({"alanine_pump": 1, "cysteine_pump": 2}, name="valve")

uv_spec = mw.Sensor(name="uv_spec")
heater = mw.TempControl(mw.Tube("5 in", "1/16 in", "2/16 in", "Metal"), name="heater")
collection_bottle = mw.Vessel("collection_bottle")

#define apparatus
A = mw.Apparatus(name="peptide_synthesizer")
A.add(alanine, alanine_pump, mw.Tube("1 in", "1/16 in", "2/16 in", "PVC"))
A.add(cysteine, cysteine_pump, mw.Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(cysteine_pump, valve, mw.Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(alanine_pump, valve, mw.Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(valve, uv_spec, mw.Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(uv_spec, heater, mw.Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(heater, collection_bottle, mw.Tube("5 in", "1/16 in", "2/16 in", "PVC"))

amino_acid_mapping = dict(C=cysteine_pump, A=alanine_pump)
P = mw.Protocol(A, duration="auto")
P.add(uv_spec, active=True)
P.add(heater, temp="60 degC")

start_time = timedelta(seconds=0)

for amino_acid in "CACA":
	P.add(amino_acid_mapping[amino_acid], start=start_time, duration="15 seconds", rate="15 ml/min")
	P.add(valve, start=start_time, duration="15 seconds", setting=amino_acid_mapping[amino_acid])
	start_time += timedelta(seconds=15)

# P.execute("http://127.0.0.1:5000/submit_protcol")
print(P.procedures)
print(P.yaml())
