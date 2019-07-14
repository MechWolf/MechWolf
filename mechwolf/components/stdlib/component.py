from warnings import warn

from loguru import logger

from . import ureg


class Component(object):
    """
    One of the individial, irreducible parts of a flow chemistry setup.

    All components in an `Apparatus` must be of type `Component`. However, it is unlikely that a user will directly
    instantiate a `Component`.

    Attributes:
    - name (str, optional): The name of the component.
    """

    _id_counter = 0
    _used_names = set()

    def __init__(self, name=None):
        # name the object, either sequentially or with a given name
        if name is None:
            self.name = self.__class__.__name__ + "_" + str(self.__class__._id_counter)
            self.__class__._id_counter += 1
        else:
            self.name = str(name)
        self._visualization_shape = "box"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

    def __str__(self):
        return f"{self.__class__.__name__} {self.name}"

    def __enter__(self):
        logger.trace(f"Entering context for {self}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.trace(f"Exiting context for {self}")
        pass

    def validate(self, dry_run):
        """Components are valid for dry runs, but not for real runs."""
        if dry_run:
            return True
        else:
            return False


class ActiveComponent(Component):
    """
    A connected, controllable component.

    All components being manipulated in a `Protocol` must be of type `ActiveComponent`.

    ::: tip
    Users should not directly instantiate an `ActiveComponent` because it is an abstract base class, not a functioning laboratory instrument.
    :::

    Attributes:
    - name (str): The name of the component.

    """

    _id_counter = 0

    def __init__(self, name=None):
        super().__init__(name=name)

    def update_from_params(self, params: dict) -> None:
        """
        Updates the attributes of the object from a dict.

        # Arguments
        - `params`: A dict whose keys are the strings of attribute names and values are the new values of the attribute.

        """
        for key, value in params.items():
            try:
                setattr(self, key, ureg.parse_expression(value))
            except BaseException:
                setattr(self, key, value)

    def base_state(self) -> dict:
        """
        A placeholder method for the base state of the component.

        All subclasses of `ActiveComponent` must implement a function that returns a dict of its base state. At the end of a protocol, the component will return to this state.

        # Returns
        A dict that has values which can be parsed into compatible units of the object's attributes, if applicable.

        # Example

        ```python
        >>> Pump.base_state()
        {"rate": "0 ml/min"}
        ```

        """
        raise NotImplementedError(
            f"Please implement the base_state() method for {self} that returns a dict."
        )

    def update(self):
        raise NotImplementedError(
            f"Please implement the update() method for {self}. "
            "This method should return a True if the update was successful and False otherwise."
        )

    def validate(self, dry_run: bool) -> bool:
        """
        Checks if a component's class is valid.

        # Arguments
        - `dry_run`: Whether this is a validation check for a dry run. Ignores the actual executability of the component.


        # Returns
        Whether the component is valid or not.
        """

        logger.debug(f"Validating {self.name}...")

        # the base_state dict must not be empty
        if not self.base_state():
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
                f"Attempting to call update() method for {self}. Entering context..."
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
        logger.debug(f"{self} is valid")

        return True
