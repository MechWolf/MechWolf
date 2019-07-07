import json
from datetime import timedelta

import pytest
import yaml

import mechwolf as mw

A = mw.Apparatus()
pump1 = mw.Pump("pump1")
pump2 = mw.Pump("pump2")
A.add(pump1, pump2, mw.Tube(length="1 foot", ID="1 in", OD="2 in", material="PVC"))


def test_create_protocol():
    # test naming
    assert mw.Protocol(A, name="testing").name == "testing"
    assert mw.Protocol(A).name == "Protocol_0"
    assert mw.Protocol(A).name == "Protocol_1"


def test_add():
    P = mw.Protocol(A)

    procedure = {"params": {"rate": "10 mL/min"}, "duration": 300}

    # test using duration
    P.add(pump1, rate="10 mL/min", duration="5 min")
    assert dict(P.procedures[pump1][0]._asdict()) == procedure

    # test adding with duration as timedelta
    P.add(pump1, rate="10 mL/min", duration=timedelta(minutes=5))
    assert dict(P.procedures[pump1][1]._asdict()) == procedure

    P = mw.Protocol(A)
    with pytest.raises(ValueError):
        P.add(mw.Pump("not in apparatus"), rate="10 mL/min", duration="5 min")

    # adding a class, not an instance of it
    with pytest.raises(ValueError):
        P.add(mw.Pump, rate="10 mL/min", duration="5 min")

    # Not adding keyword args
    with pytest.raises(RuntimeError):
        P.add(pump1, duration="5 min")

    # Invalid keyword for component
    with pytest.raises(ValueError):
        P.add(pump1, active=False, duration="5 min")

    # Invalid dimensionality for kwarg
    with pytest.raises(ValueError):
        P.add(pump1, rate="5 mL", duration="5 min")

    P.add(pump1, rate="5 mL/min")
    # don't know when the protocol will be over, so should raise error if stop
    # duration isn't provided a second time
    with pytest.raises(ValueError):
        P.add(pump1, rate="5 mL/min")


def test_compile():
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    assert P.compile() == {
        pump1: [
            mw.protocol.CompiledProcedure(params={"rate": "10 mL/min"}, start=0),
            mw.protocol.CompiledProcedure(params=pump1.base_state(), start=300),
        ],
        pump2: [
            mw.protocol.CompiledProcedure(params={"rate": "10 mL/min"}, start=0),
            mw.protocol.CompiledProcedure(params=pump2.base_state(), start=300),
        ],
    }

    # if no stop times are given, auto duration should fail
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min")
    with pytest.raises(RuntimeError):
        P.compile()

    # raise warning if component not used
    P = mw.Protocol(A)
    P.add(pump1, rate="10 mL/min", duration="5 min")
    with pytest.warns(UserWarning, match="not used"):
        P.compile()

    # check switching between rates
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    P.add(pump1, rate="5 mL/min", duration="5 min")
    assert P.compile() == {
        pump1: [
            mw.protocol.CompiledProcedure(params={"rate": "10 mL/min"}, start=0),
            mw.protocol.CompiledProcedure(params={"rate": "5 mL/min"}, start=300),
            mw.protocol.CompiledProcedure(params=pump1.base_state(), start=600),
        ],
        pump2: [
            mw.protocol.CompiledProcedure(params={"rate": "10 mL/min"}, start=0),
            mw.protocol.CompiledProcedure(params=pump2.base_state(), start=300),
        ],
    }


def test_json():
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    assert json.loads(P.json()) == {
        "pump1": [
            {"params": {"rate": "10 mL/min"}, "start": 0},
            {"params": {"rate": "0 mL/min"}, "start": 300.0},
        ],
        "pump2": [
            {"params": {"rate": "10 mL/min"}, "start": 0},
            {"params": {"rate": "0 mL/min"}, "start": 300.0},
        ],
    }


def test_yaml():
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    assert yaml.safe_load(P.yaml()) == json.loads(P.json())
