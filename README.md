<h1 align ="center">
<img src='https://github.com/MechWolf/MechWolf/raw/master/logo/head10x.png' width="150">
<br>
MechWolf
</h1>

<div align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.7-blue.svg" alt="Python version" /></a>
<a href="https://gitter.im/mechwolf-project"><img src="https://img.shields.io/badge/chat-on%20gitter-brightgreen.svg" alt="Gitter chat" /></a>
<a href="https://gitter.im/mechwolf-project"><img src="https://img.shields.io/badge/DOI-to%20be%20determined-brightgreen.svg" alt="DOI" /></a>
<a href="https://github.com/MechWolf/MechWolf/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-GPLv3-blue.svg" alt="GPLv3 license" /></a>
<img src="https://img.shields.io/travis/MechWolf/MechWolf.svg" alt="Travis status"/>
<a href="https://mechwolf.netlify.com"><img src="https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fdeveloper.oswaldlabs.com%2Fnetlify-status%2F39a2d45e-f621-4e8d-afed-3ae2ee4b9364" alt="Netlify"/></a>
<a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

</div>
<br>

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
$ pip install git+https://github.com/MechWolf/MechWolf.git
```

## What can MechWolf do?

A lot.
Let's say you're trying to automate the production of [acetaminophen](https://en.wikipedia.org/wiki/Paracetamol), a popular pain reliever and fever reducer.
The reaction involves combining two chemicals, 4-aminophenol and acetic anhydride.
The basic level of organization in MechWolf are individual components, such as the vessels and pumps.

First, we define our components and create an **`Apparatus`** object to hold them:

```python
import mechwolf as mw

# define the vessels
aminophenol = mw.Vessel("15 mL 4-aminophenol")
acetic_anhydride = mw.Vessel("15 mL acetic anhydride")
acetaminophen = mw.Vessel("acetaminophen")

# define the pumps
pump_1 = mw.Pump()
pump_2 = mw.Pump()

# define the mixer
mixer = mw.TMixer()

# same tube specs for all tubes
tube = mw.Tube(length="1 m", ID="1/16 in", OD="2/16 in", material="PVC")

# create the Apparatus object
A = mw.Apparatus()
```

Next, we define the connectivity of the **`Apparatus`** with **`add()`**. **`add()`** expects three arguments, `from_component`, `to_component`, and `tube` (in that order). First, we connect `aminophenol` to `pump_1` via `tube`:

```python
A.add(from_component=aminophenol, to_component=pump_1, tube=tube)
```

Note that the keyword arguments are optional:

```python
A.add(acetic_anhydride, pump_2, tube)
```

Since `from_component` is a list, both `pump_1` and `pump_2` will be connected to `mixer`.

```python
A.add([pump_1, pump_2], mixer, tube)
```

Finally, connect `mixer` to the output vessel, `acetaminophen`:

```python
A.add(mixer, acetaminophen, tube)
```

Then we define a **`Protocol`** and run it:

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
