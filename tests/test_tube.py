import pytest

import mechwolf as mw


def test_diameter_validation():
    # inner diameter is greater than outer diameter
    with pytest.raises(ValueError):
        mw.Tube(length="5 cm", ID="2 cm", OD="1 cm", material="boyfriend material")

def test_length_units():
    with pytest.raises(ValueError):
        mw.Tube(length="5 L", ID="1 cm", OD="3 cm", material="boyfriend material")

def test_repr():
    assert str(mw.Tube(length="5 cm", ID="1 cm", OD="2 cm", material="boyfriend material")) == "Tube of length 5 centimeter, ID 1 centimeter, OD 2 centimeter"
