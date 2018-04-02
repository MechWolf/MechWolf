Creating New Components
=======================

General Approach
----------------

You may find yourself in the position that MechWolf's included components aren't
what you need. In that case, you'll have to create your own component. Here's how:

1. **Decide what kind of component it is.**
    If you're trying to make a new kind of pump, for example, you'll want to be
    inheriting from :class:`~mechwolf.components.pump.Pump`.

2. **Create a new class.**
    If you're struggling, see `the official Python docs
    <https://docs.python.org/3/tutorial/classes.html>`_, a handy `tutorial on
    classes
    <https://www.tutorialspoint.com/python3/python_classes_objects.htm>`_, or
    look at MechWolf's source code.

3. **Give the component its attributes.**
    This means that anything that you will be using as keywords during your
    calls to :meth:`~mechwolf.Protocol.add` must be attributes. Furthermore, if
    they are quantities such as "10 mL/min", these attributes should be parsed
    Quantity objects.

4. **Give it a base state method.**
    MechWolf requires that any component being modified as part of a protocol
    have a base state which it will return to after the protocol. For things
    that turn on, this base state is usually "off". The base state method must
    return a dict with attribute as keys and settings for those attributes as
    values.

5. **Give it an update method.**
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

6. **Test thoroughly.**

7. **Contribute to GitHub** *(optional)*
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
variable mass of the solution flowing through it into gold.::

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

And finally, a way to update it. Here, we'll have to rely on our imagination::

    from mechwolf import ActiveComponent, ureg

    class PhilosophersStone(ActiveComponent):
        def __init__(self, name=None):
            super().__init__(name=name)
            self.rate = ureg.parse_expression("0 g/min")

        def base_state(self):
            return dict(rate="0 g/min")

        def update(self):
            # magic goes here
            pass
