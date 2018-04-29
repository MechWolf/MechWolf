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

    Client

        The software running on a physical :term:`component` that allows it to
        execute a :term:`protocol` sent to it by a :term:`hub`.

    Hub

        The central controller of an :term:`apparatus`. It receives a
        :term:`protocol`, communicates it to each :term:`client`, decides on a
        start time, and receives data back. A hub should have a stable internet
        connection to clients. It may be a single-purpose device (acting only as
        a hub) or share its computing resources with other tasks.

    MechWolf Resolver

        The MechWolf resolver is a lightweight internet tool that allows clients
        to find their hubs. It stores a unique ``hub_id`` and its address on its
        local network. Clients can then request the ``hub_id`` and connect
        directly to it over the local network.

    Security key

        A key consisting of six words separated by hyphens. It is used to
        generate a signature for each piece of data, allowing another device
        with the same key to confirm the authenticity of the data.

    
