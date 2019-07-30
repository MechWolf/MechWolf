from loguru import logger

from . import ureg
from .component import Component


class ActiveComponent(Component):
    """
    A connected, controllable component.

    All components being manipulated in a `Protocol` must be of type `ActiveComponent`.

    ::: tip
    Users should not directly instantiate an `ActiveComponent` because it is an abstract base class, not a functioning laboratory instrument.
    :::

    Arguments:
    - `name`: The name of the component.

    Attributes:
    - `name`: The name of the component.

    """

    _id_counter = 0

    def __init__(self, name=None):
        super().__init__(name=name)

    def update_from_params(self, params: dict) -> None:
        """
        Updates the attributes of the object from a dict.

        Arguments:
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

        All subclasses of `ActiveComponent` must implement a function that returns a dict of its base state.
        At the end of a protocol, the component will return to this state.

        Returns:
        - A dict that has values which can be parsed into compatible units of the object's attributes, if applicable.

        Example:

        ```python
        >>> Pump.base_state()
        {"rate": "0 ml/min"}
        ```
        """
        raise NotImplementedError(
            f"Please implement a base_state() method for {self} that returns a dict."
        )

    def update(self):
        raise NotImplementedError(f"Please implement an update() method for {self}.")

    def validate(self, dry_run: bool) -> None:
        """
        Checks if a component's class is valid.

        Arguments:
        - `dry_run`: Whether this is a validation check for a dry run. Ignores the actual executability of the component.


        Returns:
        - Whether the component is valid or not.
        """

        logger.debug(f"Validating {self.name}...")

        # the base_state dict must not be empty
        if not self.base_state():
            raise ValueError("base_state method dict must not be empty")

        # base_state method must return a dict
        elif not isinstance(self.base_state(), dict):
            raise ValueError("base_state method does not return a dict")

        # validate the base_state dict
        for k, v in self.base_state().items():
            if not hasattr(self, k):
                raise ValueError(
                    f"base_state sets {k} for {self} but {k} is not an attribute of {self}. "
                    f"Valid attributes are {self.__dict__}"
                )

            # dimensionality checking
            if (
                isinstance(self.__dict__[k], ureg.Quantity)
                and ureg.parse_expression(v).dimensionality
                != self.__dict__[k].dimensionality
            ):
                raise ValueError(
                    f"Invalid dimensionality in base_state for {self}. "
                    f"Got {ureg.parse_expression(v).dimensionality} for {k}, "
                    f"expected {self.__dict__[k].dimensionality}"
                )

            # if not dimensional, do type matching
            if not isinstance(self.__dict__[k], ureg.Quantity):
                if not isinstance(self.__dict__[k], type(v)):
                    raise ValueError(
                        f"Bad type matching for {k} in base_state dict. "
                        f"Should be {type(self.__dict__[k])} but is {type(v)}."
                    )

        # once we've checked everything, it should be good
        if not dry_run:
            self.update_from_params(self.base_state())
        #        logger.trace(f"Attempting to call update() for {self}. Entering context")
        #        with self:
        #            if self.update() is not None:
        #                raise ValueError("Received return value from update.")

        logger.debug(f"{self} is valid")
