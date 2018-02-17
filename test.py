from flow import Apparatus, Protocol
from components import Component, Tube, Pump, Sensor, Valve, TempControl, Vessel
from datetime import timedelta, datetime

#define the components
alanine = Vessel("15 ml fmoc-L-Alanine in 10 g of salt")
cysteine = Vessel("20 ml water")
alanine_pump = Pump(name="A")
cysteine_pump = Pump(name="C")
valve = Valve(dict(A="A", C="B"), name="valve")
uv_spec = Sensor(name="uv_spec")
heater = TempControl(Tube("5 in", "1/16 in", "2/16 in", "Metal"), name="heater")
collection_bottle = Component(name="collection_bottle")

#define apparatus
A = Apparatus(name="peptide_synthesizer")
A.add(alanine, alanine_pump, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(cysteine, cysteine_pump, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(cysteine_pump, valve, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(alanine_pump, valve, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(valve, uv_spec, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(uv_spec, heater, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
A.add(heater, collection_bottle, Tube("5 in", "1/16 in", "2/16 in", "PVC"))

amino_acid_mapping = dict(C=cysteine_pump, A=alanine_pump)
P = Protocol(A, duration="auto")
P.add(uv_spec, active=True)
P.add(heater, temp="60 degC")

start_time = timedelta(seconds=0)

for amino_acid in "CAACAAAACACACAA":
	P.add(amino_acid_mapping[amino_acid], start_time=start_time, duration="15 seconds", rate="15 ml/min")
	P.add(valve, start_time=start_time, duration="15 seconds", setting=str(amino_acid_mapping[amino_acid]))
	start_time += timedelta(seconds=15)

# print(P.json())
print(A.description())