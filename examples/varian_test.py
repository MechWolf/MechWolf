from datetime import timedelta, datetime

import mechwolf as mw

varian_pump = mw.VarianPump(name="varian_pump")
test_comp = mw.Component(name="test")

#define apparatus
A = mw.Apparatus()
A.add(test_comp, varian_pump, mw.Tube("5 in", "1/16 in", "2/16 in", "PVC"))


start_time = timedelta(seconds=0)

P = mw.Protocol(A, duration="auto")
P.add(varian_pump, start=start_time, duration="15 seconds", rate='5 mL/min')

# P.execute("http://127.0.0.1:5000/submit_protcol")
print(P.procedures)
print(P.yaml())
P.execute()
