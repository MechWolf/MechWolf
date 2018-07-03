Getting Started
===============

The best way to learn MechWolf is by example. In the spirit of reproducibility,
we are going to go through the process of setting up and running our peptoid
synthesizer step-by-step.

Create Components
-----------------

Let's start from square one (or zero, if you're counting like a programmer
[#f1]_). We first need to import MechWolf:

.. literalinclude:: ../../../examples/peptoid.py
   :language: python
   :lines: 1-2

We also imported the :class:`datetime.timedelta` class, for reasons we'll see
later. The next thing that we need to do is to define the components of our
synthesizer. It will consist of vessels containing reagents:

.. literalinclude:: ../../../examples/peptoid.py
   :language: python
   :lines: 4-8

And the amines:

.. literalinclude:: ../../../examples/peptoid.py
   :language: python
   :lines: 10-18

What we have so far are a bunch of :class:`~mechwolf.components.vessel` objects.
Note that when we instantiate them we give them two arguments. The first,
required argument is what's in it. The second ``name`` keyword is the name the
we'll be using to refer to it. Consider the ``name`` to be like a unique
identifier. In most if not all cases it should match the variable name. However,
note that the name of the vessel does not need to match what's inside it.

Now, we'll define the pumps that will drive the system:

.. literalinclude:: ../../../examples/peptoid.py
   :language: python
   :lines: 21-22

Note that the names of the objects don't match the variables! Why? Each physical
device has a unique name that is associated with it. In one apparatus, the pump
named ``pump_3`` might be the coupling pump, but in a completely different
apparatus might be something entirely different. However, we need a way uniquely
identify it so that we can send it commands during execution. It would be
annoying to have to remember the name of the phyiscal device **and** the
device's variable name, so you only need to associate them once (at definition)
and MechWolf will take care of making sure that commands get to the right place
during execution.

.. rubric:: Footnotes

.. [#f1] Which you should be. If you don't get this joke, go back and read the :doc:`gentle introduction <gentle_intro>` before proceeding.
