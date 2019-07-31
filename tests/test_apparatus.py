import pytest

import mechwolf as mw

a, b, c, d = [mw.Component() for i in range(4)]
t = mw.Tube(length="1 foot", ID="1 in", OD="2 in", material="PVC")

A = mw.Apparatus()


def test_add_basic():
    A.add(a, b, t)
    assert A.network == [(a, b, t)]
    assert A.components == {a, b}


def test_add_errors():
    with pytest.raises(ValueError):
        A.add(a, b, a)  # not using a tube

    with pytest.raises(ValueError):
        A.add(a, t, t)  # using a tube instead of a component

    with pytest.raises(ValueError):
        A.add(mw.Component, b, t)  # adding a class, not an instance of one


def test_add_multiple():
    # multiple components connected to same component in one line
    B = mw.Apparatus()
    B.add([a, b, c], d, t)
    assert B.network == [(a, d, t), (b, d, t), (c, d, t)]


def test__validate():
    # test network connectivity checking
    assert A._validate()
    with pytest.warns(UserWarning, match="connect"):
        A.add(a, b, t)
        A.add(c, d, t)
        A._validate()  # not fully connected
    A.add(b, d, t)  # fully connected
    assert A._validate()


def test_describe():
    C = mw.Apparatus()
    C.add(mw.Vessel("water"), b, t)
    assert (
        C.describe()
        == "A vessel containing water was connected to Component Component_1 using PVC tubing (length 1 foot, ID 1 inch, OD 2 inch). "
    )
