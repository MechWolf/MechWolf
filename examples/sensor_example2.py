import mechwolf as mw


# create components
a = mw.Component(name="a")
b = mw.Component(name="b")
c = mw.Component(name="c")
test = mw.DummySensor(name="test")
test2 = mw.DummySensor(name="test2")

# create apparatus
A = mw.Apparatus()
A.add([a, b, c], test, mw.Tube("1 foot", "1/16 in", "2/16 in", "PVC"))
A.add([a, b, c], test2, mw.Tube("1 foot", "1/16 in", "2/16 in", "PVC"))

P = mw.Protocol(A, duration="auto")
P.add(test, rate="5 Hz", start="5 secs", stop="10 secs")
P.add(test2, rate="5 Hz", start="5 secs", stop="20 secs")
P.add(test, rate="5 Hz", start="15 secs", stop="20 secs")
print(P.yaml())
P.execute()
