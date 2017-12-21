from flow import Apparatus, Protocol
from components import Component, Tube, Pump, Sensor

# define the components
bottle_A = Component(name="bottle_A")
bottle_B = Component(name="bottle_B")
pump0 = Pump("localhost:8888", name="pump0")
pump1 = Pump("localhost:8889", name="pump1")
manifold = Component(name="manifold")
uv_spec = Sensor("localhost:8890", name="uv_spec")
collection_bottle = Component(name="collection_bottle")

# define the configuration of the components
apparatus = Apparatus()
apparatus.add(bottle_A, pump0, Tube("50 mm", "1/16 in", "2/16 in"))
apparatus.add(bottle_B, pump1, Tube("50 mm", "1/16 in", "2/16 in"))
apparatus.add(pump0, manifold, Tube("50 mm", "1/16 in", "2/16 in"))
apparatus.add(pump1, manifold, Tube("50 mm", "1/16 inches", "2/16 in"))
apparatus.add(manifold, uv_spec, Tube("50 mm", "1/16 in", "2/16 in", temp="90 degC"))
apparatus.add(uv_spec, collection_bottle, Tube("50 mm", "1/16 in", "2/16 in"))

# check the apparatus
apparatus.summarize()
apparatus.visualize()

# define the protocol
protocol = Protocol(apparatus, duration="1 hour")
protocol.continuous(uv_spec, active=True)
protocol.add("0 secs", "1 hour", pump0, rate="20.0 ml/min")
protocol.add("0 secs", "1 hour", pump1, rate="30.0 ml/min")

protocol.compile()