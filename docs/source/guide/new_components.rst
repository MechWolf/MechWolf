Creating New Components
=======================

General Approach
----------------

You may find yourself in the position that MechWolf's included components aren't
what you need. In that case, you'll have to create your own component. Here's how:

1. **Decide what kind of component it is.**
    If you're trying to make a new kind of pump, for example, you'll want to be
    inheriting from :class:`~mechwolf.components.pump.Pump`. For components
    being controlled (i.e. not aliases of
    :class:`~mechwolf.components.component.Component`), you'll have to create a
    subclass of :class:`~mechwolf.components.component.ActiveComponent`. If you
    are only creating an alias of :func:`~mechwolf.validate_component`, you can
    skip 4–6.

2. **Create a new class.**
    If you're struggling, see `the official Python docs
    <https://docs.python.org/3/tutorial/classes.html>`_, a handy `tutorial on
    classes
    <https://www.tutorialspoint.com/python3/python_classes_objects.htm>`_, or
    look at MechWolf's source code. Make sure to add ``name`` as an argument to
    ``__init__`` and the line ``super().__init__(name=name)``, which tells
    Python to pass the name argument up to the
    :class:`~mechwolf.components.component.ActiveComponent` class.

3. **Give the component its attributes.**
    This means that anything that you will be using as keywords during your
    calls to :meth:`~mechwolf.Protocol.add` must be attributes. Furthermore, if
    they are quantities such as "10 mL/min", these attributes should be parsed
    Quantity objects.

4. **Give it a base state method.**
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

5. **Give it a config method.**
    Often times, components will require some configuration information when
    running mechwolf-setup. For example, Vici valves need to know to what serial
    port they are connected. To get this information, give your component a
    configuration method, called ``config`` that returns a dictionary whose keys
    are parameters to be confiured and whose values are tuples with the desired
    type and default value for the parameter. Going back to the Vici valve
    example, these valves usually have 10 positions, so a config dict could look
    like::

        >>> ViciValve(name="valve").config()
        {"positions": (int, None), "serial_port": (int, None)}

    Note that, when there is no default, the second value of the tuple is
    ``None``. When your component is instantiated on the client, these values
    will be passed to ``__init__()`` as keyword arguments.

6. **Give it an update method.**
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

7. **Test thoroughly with** :func:`~mechwolf.validate_component`.
    For your convenience, the :func:`~mechwolf.validate_component` function will
    take an instance of your class (not the class itself) and verify that it
    meets the requirements to be used in a protocol.

8. **Contribute to GitHub** *(optional)*
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

A Note on Naming
----------------

Be sure to follow MechWolf's naming convention, especially if you plan on
contributing to the GitHub. Classes are named in CamelCase format in keeping
with `PEP 08's class name specification
<https://www.python.org/dev/peps/pep-0008/#class-names>`_.
