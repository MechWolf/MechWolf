import mechwolf as mw

# create components
a = mw.Component(name="a")
b = mw.Component(name="b")
c = mw.Component(name="c")
test = mw.ViciValve(name="valve", mapping=dict(a=1, b=2, c=3))

# create apparatus
A = mw.Apparatus()
A.add([a, b, c], test, mw.Tube("1 foot", "1/16 in", "2/16 in", "PVC"))

# create protocol
P = mw.Protocol(A, duration="auto")
P.add(test, setting="a", start="3 secs", stop="4 secs")
P.add(test, setting="b", start="4 secs", stop="5 secs")
P.add(test, setting="c", start="5 secs", stop="6 secs")

# P.visualize()
# P.execute("http://127.0.0.1:5000/submit_protocol")
# print(P.yaml())
P.execute()
