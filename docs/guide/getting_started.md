
# Getting Started

The best way to learn MechWolf is by example. In the spirit of reproducibility,
we are going to go through the process of setting up and running our peptoid
synthesizer step-by-step.

## Create Components

Let's start from square one (or zero, if you're counting like a programmer). We first need to import MechWolf:


```python
import mechwolf as mw
```

The next thing that we need to do is to define the components of our
synthesizer. It will consist of vessels containing reagents:


```python
# define vessels
coupling_agent = mw.Vessel("DCC", name="coupling_agent")
acid = mw.Vessel("bromoacetic acid", name="acid")
solvent = mw.Vessel("solvent", name="solvent")
output = mw.Vessel("waste", name="output")
```

And the amines:


```python
# define amines
amine_1 = mw.Vessel("amine_1", name="amine_1")
amine_2 = mw.Vessel("amine_2", name="amine_2")
amine_3 = mw.Vessel("amine_3", name="amine_3")
amine_4 = mw.Vessel("amine_4", name="amine_4")
amine_5 = mw.Vessel("amine_5", name="amine_5")
amine_6 = mw.Vessel("amine_6", name="amine_6")
amine_7 = mw.Vessel("amine_7", name="amine_7")
amine_8 = mw.Vessel("amine_8", name="amine_8")
```

What we have so far are a bunch of `vessel` objects.
Note that when we instantiate them we give them two arguments. The first,
required argument is what's in it. The second `name` keyword is the name the
we'll be using to refer to it. Consider the `name` to be like a unique
identifier. In most if not all cases it should match the variable name. However,
note that the name of the vessel does not need to match what's inside it.

Now, we'll define the pumps that will drive the system:


```python
# define pumps
coupling_pump = mw.VarianPump(name="pump_3")
amine_pump = mw.VarianPump(name="pump_2")
mixer = mw.TMixer()
```

Note that the names of the objects don't match the variables! Why? Each physical
device has a unique name that is associated with it. In one apparatus, the pump
named ``pump_3`` might be the coupling pump, but in a completely different
apparatus might be something entirely different. However, we need a way uniquely
identify it so that we can send it commands during execution. It would be
annoying to have to remember the name of the phyiscal device **and** the
device's variable name, so you only need to associate them once (at definition)
and MechWolf will take care of making sure that commands get to the right place
during execution.


```python
# define valve
amine_mapping = dict(
    amine_1=1,
    amine_2=2,
    amine_3=3,
    amine_4=4,
    amine_5=5,
    amine_6=6,
    amine_7=7,
    amine_8=8,
    acid=9,
    solvent=10,
)
valve = mw.ViciValve(name="valve", mapping=amine_mapping)
```


```python
coupling_valve = mw.ViciValve(
    name="coupling_valve", mapping=dict(coupling_agent=1, solvent=10)
)
```


```python
fat_tube = mw.Tube(length="2 foot", ID="1/16 in", OD="1/8 in", material="PFA")
thin_tube = mw.Tube(length="2 foot", ID="0.04 in", OD="1/16 in", material="PFA")
```

## Create the Apparatus

Now that we have our components defined, we need to tell Mechwolf how they are connected. The `Apparatus` object will do just that. First, we create the object (calling it `A` for brevity) and give it a name as the only argument.


```python
A = mw.Apparatus("Automated Fast Flow Peptoid Synthesizer")
```

We now need to tell Mechwolf what components make up the apparatus. We do that with the `add()` function, which takes three arguments: from component(s), to component, and tube.


```python
A.add(
    coupling_agent,
    coupling_valve,
    mw.Tube(length="130 cm", ID="1/16 in", OD="1/8 in", material="PFA"),
)
A.add(solvent, coupling_valve, fat_tube)
A.add(coupling_valve, coupling_pump, fat_tube)
A.add(coupling_pump, mixer, thin_tube)
A.add(
    [
        amine_1,
        amine_2,
        amine_3,
        amine_4,
        amine_5,
        amine_6,
        amine_7,
        amine_8,
        solvent,
        acid,
    ],
    valve,
    fat_tube,
)
A.add(valve, amine_pump, fat_tube)
A.add(amine_pump, mixer, thin_tube)
```


```python
A.visualize()
```


```python
A.summarize()
```


```python
P = mw.Protocol(A, duration="auto")
```


```python
from datetime import timedelta

# let's start at the very beginning (a very good place to start)
start = timedelta(seconds=0)

# how much time to leave the pumps off before and after switching the valve
switching_time = timedelta(seconds=1)
coupling_duration = timedelta(minutes=1, seconds=30)
amine_addition_duration = timedelta(minutes=1, seconds=30)
```


```python
def add_rinse():
    global start
    rinse_duration = timedelta(minutes=2)

    P.add(
        [valve, coupling_valve], start=start, duration=rinse_duration, setting="solvent"
    )

    P.add(
        [amine_pump, coupling_pump],
        start=start + switching_time,
        duration=rinse_duration - 2 * switching_time,
        rate="5 mL/min",
    )

    start += rinse_duration
```


```python
peptoid = [
    "amine_2",
    "amine_2",
    "amine_1",
    "amine_2",
    "amine_1",
    "amine_3",
    "amine_2",
    "amine_1",
    "amine_3",
    "amine_3",
]
```

We now define


```python
for amine in peptoid:

    # initial rinse
    add_rinse()

    # perform acid coupling, first setting valve positions
    P.add(valve, start=start, duration=coupling_duration, setting="acid")
    P.add(
        coupling_valve,
        start=start,
        duration=coupling_duration,
        setting="coupling_agent",
    )
    # then turn on the pumps for the duration, leaving time on both ends for valve switching
    P.add(
        [amine_pump, coupling_pump],
        start=start + switching_time,
        duration=coupling_duration - 2 * switching_time,
        rate="5 mL/min",
    )
    start += coupling_duration

    # another rise
    add_rinse()

    # now onto amine addition, setting the main valve to the amine
    P.add(valve, start=start, duration=amine_addition_duration, setting=amine)
    # move the coupling valve to the solvent position
    P.add(
        coupling_valve, start=start, duration=amine_addition_duration, setting="solvent"
    )
    # only turn on the amine pump now, again leaving switching time
    P.add(
        amine_pump,
        start=start + switching_time,
        duration=amine_addition_duration - 2 * switching_time,
        rate="5 mL/min",
    )
    start += amine_addition_duration

    # after amine addition, wash out with just the amine pump
    P.add(valve, start=start, duration=amine_addition_duration, setting="solvent")
    P.add(
        coupling_valve, start=start, duration=amine_addition_duration, setting="solvent"
    )
    P.add(
        amine_pump,
        start=start + switching_time,
        duration=amine_addition_duration - 2 * switching_time,
        rate="5 mL/min",
    )
    start += amine_addition_duration
```


```python
add_rinse()
add_rinse()
```


```python
P.visualize()
```
