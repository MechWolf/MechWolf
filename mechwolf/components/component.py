from . import ureg


class Component(object):
    """One of the individial, irreducible parts of a flow chemistry setup.

    All components in an :class:`~mechwolf.Apparatus` must be of type
    :class:`Component`. However, it is unlikely that a user will directly
    instantiate a :class:`Component`.

    Attributes:
        name (str, optional): The name of the component.

    Raises:
        ValueError: When a component has the same name as another component.
    """

    _id_counter = 0
    _used_names = set()

    def __init__(self, name=None):
        # name the object, either sequentially or with a given name
        if name is None:
            self.name = self.__class__.__name__ + "_" + str(self.__class__._id_counter)
            self.__class__._id_counter += 1
        else:
            self.name = name
        self._visualization_shape = "box"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class ActiveComponent(Component):
    """A connected, controllable component.

    All components being manipulated in a :class:`~mechwolf.Protocol` must be of
    type :class:`ActiveComponent`.

    Note:
        Users should not directly instantiate an :class:`ActiveComponent`
        because it is an abstract base class, not a functioning laboratory
        instrument.

    Attributes:
        name (str): The name of the component.

    """

    _id_counter = 0

    def __init__(self, name):
        super().__init__(name=name)

    def update_from_params(self, params):
        """Updates the attributes of the object from a dict.

        Args:
            params (dict): A dict whose keys are the strings of attribute names and values are the new values of the attribute.

        """
        for key, value in params.items():
            try:
                setattr(self, key, ureg.parse_expression(value))
            except BaseException:
                setattr(self, key, value)

    def base_state(self):
        """A placeholder method for the base state of the component.

        All subclasses of ActiveComponent must implement a function that returns
        a dict of its base state. At the end of a protocol, the component will
        return to this state.

        Returns:
            dict: A dict that has values which can be parsed into compatible units of
            the object's attributes, if applicable.

        Example:
            >>> Pump.base_state()
            {"rate": "0 ml/min"}

        """
        pass

    def config(self):
        """A placeholder method containing the information needed to configure the component.

        When an ActiveComponent is used in the real world, there is likely
        variables that will need to be configured such as serial port. This
        method returns that information.

        Returns:
            dict: A dict of the form ``{attribute: (type, default)}``. If there is no
            default, the value should be ``(type, None)``.

        Example:
            >>> ViciValve.config()
            {"serial_port": (str, None)}

        """
        return {}

    def update(self):
        pass

    async def monitor(self):
        yield None
