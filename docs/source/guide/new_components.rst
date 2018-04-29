Creating New Components
=======================

General Approach
----------------

You may find yourself in the position that MechWolf's included components aren't
what you need. In that case, you'll have to create your own component. Here's how:

#. **Decide what kind of component it is.**
    If you're trying to make a new kind of pump, for example, you'll want to be
    inheriting from :class:`~mechwolf.components.pump.Pump`. For components
    being controlled (i.e. not aliases of
    :class:`~mechwolf.components.component.Component`), you'll have to create a
    subclass of :class:`~mechwolf.components.component.ActiveComponent`. If you
    are only creating an alias of :func:`~mechwolf.validate_component`, you can
    skip 4–6.

#. **Create a new class.**
    If you're struggling, see `the official Python docs
    <https://docs.python.org/3/tutorial/classes.html>`_, a handy `tutorial on
    classes
    <https://www.tutorialspoint.com/python3/python_classes_objects.htm>`_, or
    look at MechWolf's source code. Make sure to add ``name`` as an argument to
    ``__init__`` and the line ``super().__init__(name=name)``, which tells
    Python to pass the name argument up to the
    :class:`~mechwolf.components.component.ActiveComponent` class.

#. **Give the component its attributes.**
    This means that anything that you will be using as keywords during your
    calls to :meth:`~mechwolf.Protocol.add` must be attributes. Furthermore, if
    they are quantities such as "10 mL/min", these attributes should be parsed
    Quantity objects.

#. **Give it a base state method.**
    MechWolf requires that any component being modified as part of a protocol
    have a base state which it will return to after the protocol. For things
    that turn on, this base state is usually "off". The base state method must
    be called ``base_state`` and return a dict with attribute as keys and
    settings for those attributes as values. For a Varian pump, it could look
    like this::

        >>> VarianPump(name="pump").base_state()
        {"rate": "0 mL/min"}

    The values in the base state dictionary need to be parsable into valid
    values, the same as if they were passed as keyword arguments to
    :meth:`~mechwolf.Protocol.add`. In fact, under the hood, that is exactly
    what is happening. At the end of your protocol,
    :meth:`~mechwolf.Protocol.compile` adds a procedure for each
    :class:`~mechwolf.components.component.ActiveComponent` in the protocol to
    return to its base state.

#. **Give it a config method.**
    Often times, components will require some configuration information when
    running mechwolf-setup. For example, Varian pumps need to know to what
    serial port they are connected. To get this information, give your component
    a configuration method, called ``config`` that returns a dictionary whose
    keys are parameters to be configured and whose values are tuples with the
    desired type and default value for the parameter. Going back to the Varian
    pump example, a config dict could look like this::

        >>> VarianPump(name="pump").config()
        {"serial_port": (str, None), "max_rate": (int, None)}

    Note that, when there is no default, the second value of the tuple is
    ``None``. When your component is instantiated on the client, these values
    will be passed to ``__init__()`` as keyword arguments.

#. **Give it an update method.**
    The job of the update method is to make the object's real-world state match
    its virtual representation. This is where the hardware interfacing happens.

    Note, however, that because MechWolf objects have two distinct uses (being
    manipulated before runtime and actually used during runtime to control the
    hardware), components must be able to be instantiated without respect to
    it's real-world configuration. For example, this means that, to enforce a
    level of abstraction, you shouldn't need to know what serial port your
    client is talking to your component in order to manipulate it when creating
    your script. The object that is being run on your client *would* need to
    know that though, so the object has to be able to support both uses.

#. **Test thoroughly with** :func:`~mechwolf.validate_component`.
    For your convenience, the :func:`~mechwolf.validate_component` function will
    take an instance of your class (not the class itself) and verify that it
    meets the requirements to be used in a protocol.

#. **Contribute to GitHub** *(optional)*
    Odds are you're not the only person in the world who could use the component
    you're making. In the spirit of collaboration, we welcome any and all components
    submitted to us that are compatible with our API and encourage you to submit
    your component in a pull request.

Example: Making the Philosopher's Stone
---------------------------------------

Let's say that you discovered the `philosopher's stone
<https://en.wikipedia.org/wiki/Philosopher%27s_stone>`_, which is capable of
turning anything into gold. But that's not good enough. You want an IoT
philosopher's stone with MechWolf!

To make it work with MechWolf, we'll follow the process of creating a new
component by making a blank class that inherits from
:class:`~mechwolf.components.component.ActiveComponent`::

    from mechwolf import ActiveComponent

    class PhilosophersStone(ActiveComponent):
        def __init__(self, name=None):
            super().__init__(name=name)

For attributes, let's imagine that the philosopher's stone can convert a
variable mass of the solution flowing through it into gold::

    from mechwolf import ActiveComponent, ureg

    class PhilosophersStone(ActiveComponent):
        def __init__(self, name=None):
            super().__init__(name=name)
            self.rate = ureg.parse_expression("0 g/min")

Now we'll need a base state::

    from mechwolf import ActiveComponent, ureg

    class PhilosophersStone(ActiveComponent):
        def __init__(self, name=None):
            super().__init__(name=name)
            self.rate = ureg.parse_expression("0 g/min")

        def base_state(self):
            return dict(rate="0 g/min")

And a config method. Let's pretend that the Philosopher's Stone needs to know to
what serial port it's connected. We'll ignore the complexities of actually
connecting to it for the purposes of this tutorial, however. We'll add
``serial_port`` as an argument to ``__init__()`` and have the ``config`` method
return a dictionary saying that ``serial_port`` is an integer without a default::

    from mechwolf import ActiveComponent, ureg

    class PhilosophersStone(ActiveComponent):
        def __init__(self, name=None, serial_port=None):
            super().__init__(name=name)
            self.rate = ureg.parse_expression("0 g/min")
            self.serial_port = serial_port

        def base_state(self):
            return dict(rate="0 g/min")

        def config(self):
            return dict(serial_port=(int, None))

And finally, a way to update it. Here, we'll have to rely on our imagination::

    from mechwolf import ActiveComponent, ureg

    class PhilosophersStone(ActiveComponent):
        def __init__(self, name=None, serial_port=None):
            super().__init__(name=name)
            self.rate = ureg.parse_expression("0 g/min")
            self.serial_port = serial_port

        def base_state(self):
            return dict(rate="0 g/min")

        def config(self):
            return dict(serial_port=(int, None))

        def update(self):
            # magic goes here
            pass

Saving it as ``philosophersstone.py``, we can then use
:func:`~mechwolf.validate_component` to test if instances of the class are
valid::

    >>> import mechwolf as mw
    >>> from philosophersstone import PhilosophersStone
    >>> stone = PhilosophersStone(name="stone")
    >>> mw.validate_component(stone)
    True

:func:`~mechwolf.validate_component` returned ``True``, meaning that the
philosopher's stone class is facially valid.

Example: The Vici Valve
-----------------------

The last example, though illustrative, isn't actually a working component, since
(unfortunately) philosophers' stones don't exist. Luckily, we have the next best
thing: a Vici valve. To show how to create working components, we'll walk
through MechWolf's implementation of
:class:`~mechwolf.components.vici.ViciValve`.

First, we need to include the import statements at the top. We communicate with
Vici valves via serial on the client, but don't actually *need* the serial
package in order to instantiate a :class:`~mechwolf.components.vici.ViciValve`
object. That's because you need to be able to instantiate
:class:`~mechwolf.components.vici.ViciValve` objects on devices without the
client extras installed (which includes the serial package), such as when designing
apparatuses on your personal computer. For that reason, we wrap ``import
serial`` in a try-except clause:

.. literalinclude:: ../../../mechwolf/components/vici.py
    :lines: 3-6

Because Vici valves are subclasses of :class:`~mechwolf.components.valve.Valve`,
we also need to import :class:`~mechwolf.components.valve.Valve`. Since
``vici.py`` is in the components directory, we do a local import:

.. literalinclude:: ../../../mechwolf/components/vici.py
    :lines: 8

If we were creating the object in a different directory, we would import
:class:`~mechwolf.components.valve.Valve` the usual way::

    from mechwolf import Valve

Now that we've got the modules we'll need, let's create the class:

.. literalinclude:: ../../../mechwolf/components/vici.py
    :lines: 10-11

And we'll create an ``__init__()`` method:

.. literalinclude:: ../../../mechwolf/components/vici.py
    :pyobject: ViciValve.__init__

Note that the arguments include the ones required by
:class:`~mechwolf.components.valve.Valve` (``name`` and ``mapping``) and
``serial_port``, which is needed to connect to the physical component on the
client.

We can skip adding a base state because
:class:`~mechwolf.components.valve.Valve` already has one, meaning that
:class:`~mechwolf.components.vici.ViciValve` will inherit it automatically. We
do need to tell MechWolf about what to ask for during configuration using the
``config`` method. All we actually need to know is what the serial port is:

.. literalinclude:: ../../../mechwolf/components/vici.py
    :pyobject: ViciValve.config

.. note::

    MechWolf will automatically offer serial port suggestions during
    configuration if there is an argument called ``serial_port`` in the
    ``config`` dictionary.

Now for the important parts: we need to make the object be able to make its
real-world state match the object's state. We do that with the ``update``
method. This is the driver, the heart of the component that allows for execution:

.. literalinclude:: ../../../mechwolf/components/vici.py
    :pyobject: ViciValve.update

The exact implementation will vary from component to component, but the basic
idea is that it sends the message in a format that the component can understand.

One thing to know about serial connections is that they need to be opened and
closed. However, you don't want to open and close the connection after every
procedure, especially if you'll be doing a lot of procedures in a short
duration. Instead, you want to open the connection once at the beginning and
close it at the end when you're done with the component. MechWolf can handle
that automatically if you give it some additional information, namely functions
called ``__enter__`` and ``__exit__``.

In Vici valves, ``__enter__`` creates a serial connection once when you start
the client and then returns ``self``:

.. literalinclude:: ../../../mechwolf/components/vici.py
    :pyobject: ViciValve.__enter__

Similarly, ``__exit__`` closes the connection:

.. literalinclude:: ../../../mechwolf/components/vici.py
    :pyobject: ViciValve.__exit__

:pep:`343` has more details.

.. glossary::

    Client
        The device

    Hub
        Another device

:term:`client` is a useful tool

A Note on Naming
----------------

Be sure to follow MechWolf's naming convention, especially if you plan on
contributing to the GitHub. Classes are named in CamelCase format in keeping
with `PEP 08's class name specification
<https://www.python.org/dev/peps/pep-0008/#class-names>`_.
