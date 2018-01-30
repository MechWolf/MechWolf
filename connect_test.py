from connection import Connection, DeviceExecutor

c = Connection()
c.connect()
e = DeviceExecutor(c)

example_task = e.submit('Led0',switch=1)
example_task._state #Prints out the state

