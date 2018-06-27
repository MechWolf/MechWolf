import mechwolf as mw


# create components
a = mw.Component(name="a")
b = mw.Component(name="b")
c = mw.Component(name="c")
test = mw.Sensor(name="test")

# create apparatus
A = mw.Apparatus()
A.add([a, b, c], test, mw.Tube("1 foot", "1/16 in", "2/16 in", "PVC"))

P = mw.Protocol(A, duration="auto")
P.add(test, active=True, start="10 secs", stop="20 secs")
P.execute()