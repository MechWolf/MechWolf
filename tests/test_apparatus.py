import mechwolf as mw
import pytest

a, b, c, d = [mw.Component() for i in range(4)]
t = mw.Tube(length="1 foot", ID="1 in", OD="2 in", material="PVC")

A = mw.Apparatus()

def test_add():
    A.add(a, b, t)
    assert A.network == [(a, b, t)]
    assert A.components == {a, b}

    with pytest.raises(ValueError):
        A.add(a, b, a) # not using a tube

    with pytest.raises(ValueError):
        A.add(a, t, t) # using a tube instead of a component

def test_validate():
    # test network connectivity checking
    assert A.validate()
    with pytest.raises(Exception):
        A.add(a, b, t)
        A.add(c, d, t)
        A.validate() # not fully connected
    A.add(b, d, t) # fully connected
    assert A.validate()
