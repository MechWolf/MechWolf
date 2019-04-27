<h1 align ="center">
<img src='https://github.com/Benjamin-Lee/MechWolf/raw/master/logo/wordmark3x.png' height="150">
</h1>

<div align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.7-blue.svg?style=flat-square" alt="Python version" /></a>
<a href="https://gitter.im/mechwolf-project"><img src="https://img.shields.io/badge/chat-on%20gitter-brightgreen.svg?style=flat-square" alt="Gitter chat" /></a>
<a href="https://gitter.im/mechwolf-project"><img src="https://img.shields.io/badge/DOI-to%20be%20determined-brightgreen.svg?style=flat-square" alt="DOI" /></a>
<a href="https://github.com/Benjamin-Lee/MechWolf/blob/master/LICENSE"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square" alt="GPLv3 license" /></a>
<img src="https://img.shields.io/travis/Benjamin-Lee/MechWolf.svg?style=flat-square" alt="Python version" /></p>
</div>

>Continuous flow process description, analysis, and automation

MechWolf is a Python framework for automating continuous flow processes.
It was developed as a collaboration between computer scientists, chemists, and complete novices to be used by anyone wanting to do better, faster, more reproducible flow-based science.
Features include:

- Natural language description, analysis, and visualization of continuous flow networks
- Automated execution of protocols
- Full user extensibility
- Smart default settings, designed by scientists for scientists
- Extensive checking to prevent potentially costly and dangerous errors before runtime
- Natural language parsing of times and quantities
- Thorough documentation and tutorials

## Installation

It's as easy as:

```bash
$ pip install mechwolf
```

Or, to get the latest (but not necessarily stable) development branch:

```bash
$ pip install git+https://github.com/Benjamin-Lee/MechWolf.git
```

## What can MechWolf do?

A lot.
Let's say you're trying to automate the production of [acetaminophen](https://en.wikipedia.org/wiki/Paracetamol), a popular pain reliever and fever reducer.
The reaction involves combining two chemicals, 4-aminophenol and acetic anhydride.
The basic level of organization in MechWolf are individual components, such as the vessels and pumps.

First, we create an `Apparatus` object:

```python
import mechwolf as mw

# define the vessels
aminophenol = mw.Vessel(description="15 mL 4-aminophenol", name="aminophenol")
acetic_anhydride = mw.Vessel("15 mL acetic anhydride", name="acetic anhydride")
acetaminophen = mw.Vessel("acetaminophen", name="acetaminophen")

# define the pumps
pump_1 = mw.Pump(name="pump_1")
pump_2 = mw.Pump(name="pump_2")

# define the mixer
mixer = mw.TMixer()

# same tube specs for all tubes
tube = mw.Tube(length="1 m",
               ID="1/16 in",
               OD="2/16 in",
               material="PVC")

# create the Apparatus object
A = mw.Apparatus()

# add the connections
A.add(aminophenol, pump_1, tube) # connect vessel_1 to pump_1
A.add(acetic_anhydride, pump_2, tube) # connect vessel_2 to pump_2
A.add([pump_1, pump_2], mixer, tube) # connect pump_1 and pump_2 to mixer
A.add(mixer, acetaminophen, tube) # connect mixer to vessel_3
```

Then we define a protocol and run it:

```python
# create the Protocol object
P = mw.Protocol(A, name="acetaminophen synthesis")
P.add([pump_1, pump_2], duration="15 mins", rate="1 mL/min")

# execute the Protocol
P.execute()
```

That's it! You can do this and a whole lot more with MechWolf.
To learn more, take a look at the [docs](example.com).

## Documentation

[Link will go here](example.com)

## License

[GPLv3](LICENSE) [(summary)](https://choosealicense.com/licenses/gpl-3.0/).

## Citation

```
Will go here.
```
