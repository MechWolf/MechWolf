from flow import Apparatus, Protocol
from components import Component, Tube, Pump, Sensor, Valve

# define the components
bottle_A = Component(name="bottle_A")
bottle_B = Component(name="bottle_B")
bottle_C = Component(name="bottle_C")
pump0 = Pump("localhost:8888")
pump1 = Pump("localhost:8889")
pump2 = Pump("localhost:8889")
valve = Valve("localhost:8999", dict(Pump_0="A", Pump_1="B", Pump_2="C"))
uv_spec = Sensor("localhost:8890", name="uv_spec")
collection_bottle = Component(name="collection_bottle")

# define the configuration of the components
apparatus = Apparatus()
apparatus.add(bottle_A, pump0, Tube("50 mm", "1/16 in", "2/16 in"))
apparatus.add(bottle_B, pump1, Tube("50 mm", "1/16 in", "2/16 in"))
apparatus.add(pump0, valve, Tube("50 mm", "1/16 in", "2/16 in"))
apparatus.add(pump1, valve, Tube("50 mm", "1/16 inches", "2/16 in"))
apparatus.add(valve, uv_spec, Tube("50 mm", "1/16 in", "2/16 in", temp="90 degC"))
apparatus.add(uv_spec, collection_bottle, Tube("50 mm", "1/16 in", "2/16 in"))

apparatus.add(bottle_C, pump2, Tube("50 mm", "1/16 in", "2/16 in"))
apparatus.add(pump2, valve, Tube("50 mm", "1/16 in", "2/16 in"))

# check the apparatus
# apparatus.compile()
# apparatus.summarize()
# apparatus.visualize()

# define the protocol
protocol = Protocol(apparatus, duration="1 min")
protocol.add(uv_spec, active=True)
protocol.add(pump0, rate="20.0 ml/min", stop_time="30 secs")

protocol.add(valve, setting="Pump_0", stop_time="30 secs")
protocol.add(valve, setting="Pump_1", start_time="30 secs")

protocol.add(pump1, rate="30.0 ml/min", start_time="30 secs")


protocol.visualize()
# print(protocol.json())