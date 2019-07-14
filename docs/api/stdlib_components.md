---
sidebarDepth: 2
editLink: false
---
# Component Standard Library
## Component
of the individial, irreducible parts of a flow chemistry setup.

All components in an :class:`~mechwolf.Apparatus` must be of type
:class:`Component`. However, it is unlikely that a user will directly
instantiate a :class:`Component`.

Attributes:
    name (str, optional): The name of the component.

Raises:
    ValueError: When a component has the same name as another component.
### validate

```python
validate(self, dry_run)
```
ts are valid for dry runs, but not for real ru

## ActiveComponent
nnected, controllable component.

All components being manipulated in a :class:`~mechwolf.Protocol` must be of
type :class:`ActiveComponent`.

Note:
    Users should not directly instantiate an :class:`ActiveComponent`
    because it is an abstract base class, not a functioning laboratory
    instrument.

Attributes:
    name (str): The name of the component.
### update_from_params

```python
update_from_params(self, params)
```
the attributes of the object from a dict.


    params (dict): A dict whose keys are the strings of attribute names and values are the new values of the attribute.

### base_state

```python
base_state(self)
```
older method for the base state of the component.

All subclasses of ActiveComponent must implement a function that returns
a dict of its base state. At the end of a protocol, the component will
return to this state.

Returns:
    dict: A dict that has values which can be parsed into compatible units of
    the object's attributes, if applicable.

Example:
    >>> Pump.base_state()
    {"rate": "0 ml/min"}

### validate

```python
validate(self, dry_run)
```
f a component's class is valid.

Arguments:
    dry_run (bool): Whether this is a validation check for a dry run. Ignores the actual executability of the component.


Returns:
    bool: True if valid, else False.

## Pump
neric pumping device whose primary feature is that it moves fluid.

Note:
    Users should not directly instantiate an :class:`Pump` for use in a :class:`~mechwolf.Protocol` becuase
    it is not an actual laboratory instrument.

Attributes:
    name (str, optional): The name of the pump.
    rate (str): The flow rate of the pump. Must be of the dimensionality of volume/time. Converted to a Quantity.
### base_state

```python
base_state(self)
```
to 0 mL/m

## DummyPump
ke pumping device whose primary feature is that it moves fluid.

Note:
    Users should not directly instantiate an :class:`Pump` for use in a :class:`~mechwolf.Protocol` becuase
    it is not an actual laboratory instrument.

Attributes:
    name (str, optional): The name of the pump.
    rate (str): The flow rate of the pump. Must be of the dimensionality of volume/time. Converted to a Quantity.
## Mixer
neric mixer.

This is an alias of :class:`~mechwolf.Component`.

Attributes:
    name (str, optional): The name of the mixer.
### __init__

```python
__init__(self, name=None)
```
r.

 is an alias of :class:`~mechwolf.Component`.

ibutes:
name (str, optional): The name of the mixer.

## TMixer
mixer.

This is an alias of :class:`~mechwolf.Component`.

Attributes:
    name (str, optional): The name of the mixer.
### __init__

```python
__init__(self, name=None)
```
r.

 is an alias of :class:`~mechwolf.Component`.

ibutes:
name (str, optional): The name of the mixer.

## YMixer
mixer.

This is an alias of :class:`~mechwolf.Component`.

Attributes:
    name (str, optional): The name of the mixer.
### __init__

```python
__init__(self, name=None)
```
mixer.

 is an alias of :class:`~mechwolf.Component`.

ibutes:
name (str, optional): The name of the mixer.

## CrossMixer
oss mixer.

This is an alias of :class:`~mechwolf.Component`.

Attributes:
    name (str, optional): The name of the mixer.

