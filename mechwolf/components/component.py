from warnings import warn

from loguru import logger

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

    def validate(self, dry_run):
        """Components are valid for dry runs, but not for real runs."""
        if dry_run:
            return True
        else:
            return False


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
        raise NotImplementedError(
            f"Please implement the base_state() method for {self} that returns a dict."
        )

    def update(self):
        raise NotImplementedError(
            f"Please implement the update() method for {self}. "
            "This method should return a True if the update was successful and False otherwise."
        )

    def validate(self, dry_run):
        """Checks if a component's class is valid.

        Arguments:
            dry_run (bool): Whether this is a validation check for a dry run. Ignores the actual executability of the component.


        Returns:
            bool: True if valid, else False.
        """

        logger.debug(f"Validating {self.name}...")

        # ensure is an ActiveComponent
        if not issubclass(self.__class__, ActiveComponent):
            warn(f"{self} is not an instance of ActiveComponent")
            return False

        # the base_state dict must not be empty
        elif not self.base_state():
            warn("base_state method dict must not be empty")
            return False

        # base_state method must return a dict
        elif not isinstance(self.base_state(), dict):
            warn("base_state method does not return a dict")
            return False

        # validate the base_state dict
        for k, v in self.base_state().items():
            if not hasattr(self, k):
                warn(
                    f"Invalid attribute {k} for {self}. Valid attributes are {self.__dict__}"
                )
                return False
            if (
                isinstance(self.__dict__[k], ureg.Quantity)
                and ureg.parse_expression(v).dimensionality
                != self.__dict__[k].dimensionality
            ):
                warn(
                    f"Invalid dimensionality {ureg.parse_expression(v).dimensionality} for {k} for {self}."
                )
                return False
            elif not isinstance(self.__dict__[k], ureg.Quantity) and not isinstance(
                self.__dict__[k], type(v)
            ):
                warn(
                    f"Bad type matching for {k} in base_state dict. Should be {type(self.__dict__[k])} but is {type(v)}."
                )
                return False

        # once we've checked everything, it should be good
        if not dry_run:
            self.update_from_params(self.base_state())
            logger.trace(
                f"Attempting to call update() method for {self.name}. Entering context..."
            )
            with self:
                logger.trace("Context entered. Calling update()")
                if not self.update():
                    warn(
                        f"Failed to set {self} to base state. Aborting before execution."
                    )
                    return False
                logger.trace("Update successful")
            logger.trace("Context exited successfully")
        logger.debug(f"{self.name} is valid")

        return True
