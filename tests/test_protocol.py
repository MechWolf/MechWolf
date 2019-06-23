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


def test_protocol_duration():
    assert str(mw.Protocol(A, duration="1 hour").duration) == "1 hour"
    with pytest.raises(ValueError):
        mw.Protocol(A, duration="1 mL")


def test_add():
    P = mw.Protocol(A, duration="auto")

    procedure = {
        "component": pump1,
        "params": {"rate": "10 mL/min"},
        "start": mw.ureg.parse_expression("0 seconds"),
        "stop": mw.ureg.parse_expression("5 minutes"),
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

    # Providing stop and duration should raise error
    with pytest.raises(RuntimeError):
        P.add(pump1, rate="5 mL/min", stop="5 min", duration="5 min")

    # don't know when the protocol will be over, so should raise error if stop
    # time/duration isn't provided
    with pytest.raises(RuntimeError):
        P.add(pump1, rate="5 mL/min")


def test_compile():
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    assert P.compile() == {
        pump1: [
            {
                "params": {"rate": "10 mL/min"},
                "time": mw.ureg.parse_expression("0 seconds"),
            },
            {"params": {"rate": "0 mL/min"}, "time": mw.ureg.parse_expression("5 min")},
        ],
        pump2: [
            {
                "params": {"rate": "10 mL/min"},
                "time": mw.ureg.parse_expression("0 seconds"),
            },
            {"params": {"rate": "0 mL/min"}, "time": mw.ureg.parse_expression("5 min")},
        ],
    }

    # auto duration parsing shouldn't change anything
    P = mw.Protocol(A, duration="auto")
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    assert P.compile() == {
        pump1: [
            {
                "params": {"rate": "10 mL/min"},
                "time": mw.ureg.parse_expression("0 seconds"),
            },
            {"params": {"rate": "0 mL/min"}, "time": mw.ureg.parse_expression("5 min")},
        ],
        pump2: [
            {
                "params": {"rate": "10 mL/min"},
                "time": mw.ureg.parse_expression("0 seconds"),
            },
            {"params": {"rate": "0 mL/min"}, "time": mw.ureg.parse_expression("5 min")},
        ],
    }

    # if no stop times are given, auto duration should fail
    P = mw.Protocol(A, duration="auto")
    P.add([pump1, pump2], rate="10 mL/min")
    with pytest.raises(RuntimeError):
        P.compile()

    # raise warning if component not used
    P = mw.Protocol(A, duration="auto")
    P.add(pump1, rate="10 mL/min", duration="5 min")
    with pytest.warns(UserWarning, match="not used"):
        P.compile()

    # check switching between rates
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    P.add(pump1, rate="5 mL/min", start="5 min", stop="10 min")
    assert P.compile() == {
        pump1: [
            {
                "params": {"rate": "10 mL/min"},
                "time": mw.ureg.parse_expression("0 seconds"),
            },
            {"params": {"rate": "5 mL/min"}, "time": mw.ureg.parse_expression("5 min")},
            {
                "params": {"rate": "0 mL/min"},
                "time": mw.ureg.parse_expression("10 min"),
            },
        ],
        pump2: [
            {
                "params": {"rate": "10 mL/min"},
                "time": mw.ureg.parse_expression("0 seconds"),
            },
            {"params": {"rate": "0 mL/min"}, "time": mw.ureg.parse_expression("5 min")},
        ],
    }

    # stop time before start time
    P = mw.Protocol(A)
    P.add([pump1, pump2], rate="10 mL/min", start="5 min", stop="4 min")
    with pytest.raises(RuntimeError):
        P.compile()

    # procedure duration longer than protocol duration
    P = mw.Protocol(A, duration="1 min")
    P.add([pump1, pump2], rate="10 mL/min", stop="4 min")
    with pytest.raises(ValueError):
        P.compile()

    # procedure start not in protocol duration
    P = mw.Protocol(A, duration="1 min")
    P.add([pump1, pump2], rate="10 mL/min", start="4 min")
    with pytest.raises(ValueError):
        P.compile()

    # raise inferring stop time warning when a procedure doesn't have a stop
    # time or duration but hte next added procedure has a start time
    P = mw.Protocol(A, duration="10 min")
    P.add([pump1, pump2], rate="10 mL/min")
    P.add([pump1, pump2], start="5 min", rate="1 mL/min")
    with pytest.warns(UserWarning, match="inferring stop time"):
        P.compile()


def test_json():
    P = mw.Protocol(A, duration="auto")
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    assert json.loads(P.json()) == {
        "pump1": [
            {"params": {"rate": "10 mL/min"}, "time": 0.0},
            {"params": {"rate": "0 mL/min"}, "time": 300.0},
        ],
        "pump2": [
            {"params": {"rate": "10 mL/min"}, "time": 0.0},
            {"params": {"rate": "0 mL/min"}, "time": 300.0},
        ],
    }


def test_yaml():
    P = mw.Protocol(A, duration="auto")
    P.add([pump1, pump2], rate="10 mL/min", duration="5 min")
    assert yaml.load(P.yaml()) == json.loads(P.json())
