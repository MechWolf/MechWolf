import asyncio
from typing import Any, Dict

from loguru import logger

from . import _ureg
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
        self._base_state: Dict[str, Any] = NotImplemented
        """
        A placeholder for the base state of the component.
        All subclasses of `ActiveComponent` must have this attribute.
        The dict must have values which can be parsed into compatible units of the object's other attributes, if applicable.
        At the end of a protocol and when not under explicit control by the user, the component will return to this state.
        """

    def _update_from_params(self, params: dict) -> None:
        """
        Updates the attributes of the object from a dict.

        Arguments:
        - `params`: A dict whose keys are the strings of attribute names and values are the new values of the attribute.
        """
        for key, value in params.items():
            if isinstance(getattr(self, key), _ureg.Quantity):
                setattr(self, key, _ureg.parse_expression(value))
            else:
                setattr(self, key, value)

    async def _update(self):
        raise NotImplementedError(f"Implement an _update() method for {repr(self)}.")

    def _validate(self, dry_run: bool) -> None:
        """
        Checks if a component's class is valid.

        Arguments:
        - `dry_run`: Whether this is a validation check for a dry run. Ignores the actual executability of the component.

        Returns:
        - Whether the component is valid or not.
        """

        logger.debug(f"Validating {self.name}...")

        # base_state method must return a dict
        if not isinstance(self._base_state, dict):
            raise ValueError("_base_state is not a dict")

        # the base_state dict must not be empty
        if not self._base_state:
            raise ValueError("_base_state dict must not be empty")

        # validate the base_state dict
        for k, v in self._base_state.items():
            if not hasattr(self, k):
                raise ValueError(
                    f"base_state sets {k} for {repr(self)} but {k} is not an attribute of {repr(self)}. "
                    f"Valid attributes are {self.__dict__}"
                )

            # dimensionality checking
            if isinstance(self.__dict__[k], _ureg.Quantity):
                # figure out the dimensions we're comparing
                expected_dim = _ureg.parse_expression(v).dimensionality
                actual_dim = self.__dict__[k].dimensionality

                if expected_dim != actual_dim:
                    raise ValueError(
                        f"Invalid dimensionality in _base_state for {repr(self)}. "
                        f"Got {_ureg.parse_expression(v).dimensionality} for {k}, "
                        f"expected {self.__dict__[k].dimensionality}"
                    )

            # if not dimensional, do type matching
            elif not isinstance(self.__dict__[k], type(v)):
                raise ValueError(
                    f"Bad type matching for {k} in _base_state dict. "
                    f"Should be {type(self.__dict__[k])} but is {type(v)}."
                )

        # once we've checked everything, it should be good
        if not dry_run:
            self._update_from_params(self._base_state)
            logger.trace(f"Attempting to call _update() for {repr(self)}.")
            with self:
                res = asyncio.run(self._update())
                if res is not None:
                    raise ValueError(f"Received return value {res} from update.")

        logger.debug(f"{repr(self)} is valid")
