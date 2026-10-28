import nbformat
import pytest
from nbclient import NotebookClient

# Most protocols are run from Jupyter, where MechWolf applies nest_asyncio
# at import and schedules the run on the kernel's event loop instead of
# calling asyncio.run(), so that path needs its own test.

RUN_PROTOCOL = """
import asyncio

from loguru import logger

import mechwolf as mw

# in a notebook MechWolf logs to a widget, so keep a copy to show on failure
log = []
logger.add(log.append, level="TRACE")

a = mw.Vessel(name="a", description="nothing")
pump = mw.DummyPump(name="Dummy pump")
sensor = mw.DummySensor(name="sensor")
tube = mw.Tube("1 foot", "1/16 in", "2/16 in", "PVC")

A = mw.Apparatus()
A.add(a, pump, tube)
A.add(pump, sensor, tube)

P = mw.Protocol(A, name="notebook execution")
P.add(pump, rate="5 mL/min", start="0 seconds", stop="3 secs")
P.add(sensor, rate="5 Hz", start="0 secs", stop="3 secs")

P.visualize()

E = P.execute(confirm=True, dry_run={dry_run}, log_file=None, data_file=None)
"""

CHECK_RESULT = """
for _ in range(300):
    if E.was_executed:
        break
    await asyncio.sleep(0.1)

assert E.was_executed
assert len(E.data["sensor"]) >= 5, "".join(str(line) for line in log[-30:])
if {dry_run}:
    assert E.data["sensor"][0].data == "simulated read"
else:
    # the dummy sensor returns a random walk
    assert all(isinstance(d.data, float) for d in E.data["sensor"]), E.data
"""


@pytest.mark.parametrize("dry_run", [True, False])
def test_protocol_runs_in_a_notebook(dry_run):
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_code_cell(RUN_PROTOCOL.format(dry_run=dry_run)),
        nbformat.v4.new_code_cell(CHECK_RESULT.format(dry_run=dry_run)),
    ]
    NotebookClient(nb, timeout=120, kernel_name="python3").execute()
