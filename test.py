from flow import Apparatus, Protocol
from components import Component, Tube, Pump, Sensor, Valve
from datetime import timedelta, datetime

#define the components
alanine = Component(name="alanine")
cysteine = Component(name="cysteine")
alanine_pump = Pump("0.0.0.0", name="alanine_pump")
cysteine_pump = Pump("0.0.0.1", name="cysteine_pump")
valve = Valve("0.0.0.2", dict(cysteine_pump="A", alanine_pump="B"), name="valve")
uv_spec = Sensor("0.0.0.3", name="uv_spec")
collection_bottle = Component(name="collection_bottle")

#define apparatus
peptide_synthesizer = Apparatus(name="peptide_synthesizer")
peptide_synthesizer.add(alanine, alanine_pump, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
peptide_synthesizer.add(cysteine, cysteine_pump, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
peptide_synthesizer.add(cysteine_pump, valve, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
peptide_synthesizer.add(alanine_pump, valve, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
peptide_synthesizer.add(valve, uv_spec, Tube("5 in", "1/16 in", "2/16 in", "PVC"))
peptide_synthesizer.add(uv_spec, collection_bottle, Tube("5 in", "1/16 in", "2/16 in", "PVC"))

# peptide_synthesizer.summarize()

amino_acid_mapping = dict(C=cysteine_pump, A=alanine_pump)
protocol = Protocol(peptide_synthesizer, duration="auto")
protocol.add(uv_spec, active=True)

start_time = timedelta(seconds=0)

for amino_acid in "CAACAAAACACACAA":
	protocol.add(amino_acid_mapping[amino_acid], start_time=start_time, duration="15 seconds", rate="15 ml/min")
	protocol.add(valve, start_time=start_time, duration="15 seconds", setting=str(amino_acid_mapping[amino_acid]))

	start_time += timedelta(seconds=15)

# print(protocol.json())
protocol.execute()