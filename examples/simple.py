import mechwolf as mw

a = mw.Component(name="a")
b = mw.Component(name="b")
c = mw.Component(name="c")
# input_vessel = Vessel("`glucose`, `indium(iii) bromide`, and `triflic acid` in a 50/50 mix of `chloroform` and `acetonitrile`", resolve=False)
test = mw.Valve(name="test_1", mapping=dict(a=1, b=2, c=3))
# test2 = Valve(name="test_2", mapping=dict(a=1, b=2, c=3))

A = mw.Apparatus()
A.add(a, test, mw.Tube("1 foot", "1/16 in", "2/16 in", "PVC"))
A.add(b, test, mw.Tube("1 foot", "1/16 in", "2/16 in", "PVC"))
A.add(c, test, mw.Tube("1 foot", "1/16 in", "2/16 in", "PVC"))
# A.add(test, test2, Tube("1 foot", "1/16 in", "2/16 in", "PVC"))


P = mw.Protocol(A, duration="auto")
P.add(test, setting="a", start="3 secs", stop="4 secs")
P.add(test, setting="b", start="4 secs", stop="5 secs")
P.add(test, setting="c", start="5 secs", stop="6 secs")
# P.add(test2, active=True)
P.visualize()
# P.execute("http://127.0.0.1:5000/submit_protocol")
# print(P.compile())
