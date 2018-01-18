from flow import Apparatus, Protocol
from components import ActiveComponent, Component, Tube
from datetime import timedelta, datetime

class Led(ActiveComponent):
	
	def __init__(self, address, name=None):
			super(Led, self).__init__(address, name=name)
			self.on = False


led = Led("address goes here")

blinky = Apparatus(name="blinky")
blinky.add(led, Component(), Tube("0 mm", "0 mm", "1 mm"))

protocol = Protocol(blinky)

protocol.add(led, stop_time="3 seconds", on=True)
protocol.add(led, start_time="3 seconds", stop_time="6 seconds", on=False)
protocol.add(led, start_time="6 seconds", stop_time="9 seconds", on=True)

print(protocol.yaml())