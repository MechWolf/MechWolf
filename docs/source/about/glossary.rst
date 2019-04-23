Glossary
========

.. glossary::

    Component

        A device that is a part of a flow system, such as a
        :class:`~mechwolf.components.vessel.Vessel` or
        :class:`~mechwolf.components.pump.Pump`. Implemented by
        :class:`~mechwolf.components.component.Component` and its children.

    Apparatus

        A unique configuration of components. Implemented by
        :class:`~mechwolf.Apparatus`.

    Procedure

        An individual, irreducible step of a protocol, such as turning a valve
        to a specific position for a specific duration.

    Protocol

        A list of procedures specified for a given apparatus. Implemented by
        :class:`~mechwolf.Protocol`.

    Compilation

        Converting the high-level description of a :term:`protocol` into a
        low-level list of steps that unambiguously tells each :term:`component`
        what to do at all times.
