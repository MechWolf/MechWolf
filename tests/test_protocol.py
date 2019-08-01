import json
from datetime import timedelta

import pytest
import yaml

import mechwolf as mw

A = mw.Apparatus()
pump1 = mw.Pump(name="pump1")
pump2 = mw.Pump(name="pump2")
tube = mw.Tube(length="1 foot", ID="1 in", OD="2 in", material="PVC")
A.add(pump1, pump2, tube)


def test_create_protocol():
    # test naming
    assert mw.Protocol(A, name="testing").name == "testing"
    assert mw.Protocol(A).name == "Protocol_0"
    assert mw.Protocol(A).name == "Protocol_1"


def test_add():
    P = mw.Protocol(A)

    procedure = {
        "component": pump1,
        "params": {"rate": "10 mL/min"},
        "start": 0,
        "stop": 300,
    }

    # test using duration
    P.add(pump1, rate="10 mL/min", duration="5 min")
    assert P.procedures[0] == procedure

    # test adding with start and stop
    P.procedures = []
    P.add(pump1, rate="10 mL/min", start="0 min", stop="5 min")
    assert P.procedures[0] == procedure

    # test adding with start and stop as timedeltas
    P.procedures = []
    P.add(
        pump1, rate="10 mL/min", start=timedelta(seconds=0), stop=timedelta(minutes=5)
    )
    assert P.procedures[0] == procedure

    # test adding with duration as timedelta
    P.procedures = []
    P.add(pump1, rate="10 mL/min", duration=timedelta(minutes=5))
    assert P.procedures[0] == procedure

    P = mw.Protocol(A)
    with pytest.raises(KeyError):
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

    # No unit
    with pytest.raises(ValueError):
        P.add(pump1, rate="5", duration="5 min")

    # Just the raw value without a unit
    with pytest.raises(ValueError):
        P.add(pump1, rate=5, duration="5 min")

    # Providing stop and duration should raise error
    with pytest.raises(RuntimeError):
        P.add(pump1, rate="5 mL/min", stop="5 min", duration="5 min")

    # stop time before start time
    with pytest.raises(ValueError):
        P.add([pump1, pump2], rate="10 mL/min", start="5 min", stop="4 min")


def test_add_dummy():
    A = mw.Apparatus()
    dummy = mw.Dummy(name="dummy")
    A.add(dummy, mw.Vessel(), tube)
    P = mw.Protocol(A)
    with pytest.raises(ValueError):
        P.add(dummy, active=1)  # should be a bool!


def test_add_valve():
    A = mw.Apparatus()
    valve = mw.Valve(mapping={pump1: 1, pump2: 2})
    bad_valve = mw.Valve()
    A.add([pump1, pump2], [valve, bad_valve], tube)
    P = mw.Protocol(A)

    expected = [dict(start=0, stop=None, component=valve, params={"setting": 1})]

    # directly pass the pump object
    P.add(valve, setting=pump1)
    assert P.procedures == expected
    P.clear_procedures()

    # using its name
    P.add(valve, setting="pump1")
    assert P.procedures == expected
    P.clear_procedures()

    # using its port number
    P.add(valve, setting=1)
    assert P.procedures == expected

    with pytest.raises(ValueError):
        P.add(valve, setting=3)

    with pytest.raises(ValueError):
        P.add(bad_valve, setting=3)


def test_compile():
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    assert P._compile() == {
        pump1: [
            {"params": {"rate": "10 mL/min"}, "time": 0},
            {"params": {"rate": "0 mL/min"}, "time": 300},
        ],
        pump2: [
            {
                "params": {"rate": "10 mL/min"},
                "time": mw._ureg.parse_expression("0 seconds"),
            },
            {"params": {"rate": "0 mL/min"}, "time": 300},
        ],
    }

    # if no stop times are given, duration inference should fail
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min")
    with pytest.raises(RuntimeError):
        P._compile()


def test_unused_component():
    # raise warning if component not used
    P = mw.Protocol(A)
    P.add(pump1, rate="10 mL/min", duration="5 min")
    with pytest.warns(UserWarning, match="not used"):
        P._compile()


def test_switching_rates():
    # check switching between rates
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    P.add(pump1, rate="5 mL/min", start="5 min", stop="10 min")
    assert P._compile() == {
        pump1: [
            {"params": {"rate": "10 mL/min"}, "time": 0},
            {"params": {"rate": "5 mL/min"}, "time": 300},
            {"params": {"rate": "0 mL/min"}, "time": 600},
        ],
        pump2: [
            {"params": {"rate": "10 mL/min"}, "time": 0},
            {"params": {"rate": "0 mL/min"}, "time": 300},
        ],
    }


def test_overlapping_procedures():
    P = mw.Protocol(A)
    P.add(pump1, start="0 seconds", stop="5 seconds", rate="5 mL/min")
    P.add(pump1, start="2 seconds", stop="5 seconds", rate="2 mL/min")
    with pytest.raises(RuntimeError):
        P._compile()


def test_conflicting_continuous_procedures():
    P = mw.Protocol(A)
    P.add(pump1, rate="5 mL/min")
    P.add(pump1, rate="2 mL/min")
    with pytest.raises(RuntimeError):
        P._compile()


def test_json():
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    assert json.loads(P.json()) == [
        {
            "start": 0,
            "stop": 300,
            "component": "pump1",
            "params": {"rate": "10 mL/min"},
        },
        {
            "start": 0,
            "stop": 300,
            "component": "pump2",
            "params": {"rate": "10 mL/min"},
        },
    ]


def test_yaml():
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    assert yaml.safe_load(P.yaml()) == json.loads(P.json())
