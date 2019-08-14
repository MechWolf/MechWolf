import mechwolf as mw

# create components
a = mw.Vessel(name="a", description="nothing")
b = mw.Vessel(name="b", description="nothing")
c = mw.Vessel(name="c", description="nothing")

pump = mw.DummyPump(name="Dummy pump")


test = mw.DummySensor(name="test")
test2 = mw.DummySensor(name="test2")
test3 = mw.DummySensor(name="test3")
test4 = mw.BrokenDummySensor(name="test4")

tube = mw.Tube("1 foot", "1/16 in", "2/16 in", "PVC")

# create apparatus
A = mw.Apparatus()
A.add([a, b, c], pump, tube)
A.add(pump, [test, test2, test3, test4], tube)

P = mw.Protocol(A, name="testing execution")
P.add(pump, rate="5 mL/min", start="0 seconds", stop="1 secs")
P.add([test, test2, test3, test4], rate="5 Hz", start="0 secs", stop="1 secs")

# test both execution modes
for dry_run in [True, False]:
    E = P.execute(confirm=True, dry_run=dry_run, log_file=None, data_file=None)
    assert len(E.data["test"]) == 5
    if dry_run:
        assert E.data["test"][0].data == "simulated read"
    assert pump.rate == mw._ureg.parse_expression(pump._base_state["rate"])

# test fast forward
E = P.execute(confirm=True, dry_run=5, log_file=None, data_file=None)
assert len(E.data["test"]) == 1
