from flow import Apparatus, Protocol
from components import ActiveComponent, Component, Tube
from datetime import timedelta, datetime

class Led(ActiveComponent):
	
	def __init__(self, address, name=None):
			super(Led, self).__init__(address, name=name)
			self.active = False

	def base_state(self):
		return dict(active=False)


led = Led("Led_0")

blinky = Apparatus(name="blinky")
blinky.add(led, Component(), Tube("0 mm", "0 mm", "1 mm", "PVC"))

protocol = Protocol(blinky)

protocol.add(led, stop_time="3 seconds", active=True)
protocol.add(led, start_time="3 seconds", stop_time="6 seconds", active=False)
protocol.add(led, start_time="6 seconds", stop_time="9 seconds", active=True)

print(protocol.json())
tasks = protocol.execute()