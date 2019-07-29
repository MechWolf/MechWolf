from math import pi
from warnings import warn

from . import ureg


class Tube(object):
    """A tube.

    Arguments:
    - `length`: The length of the tube as a str.
    - `ID`: The inner diameter of the tube as a str.
    - `OD`: The outer diameter of the tube as a str.
    - `material`: The material of the tube.

    Attributes:
    - `ID`: The inner diameter of the tube, converted to a `pint.Quantity`.
    - `length`: The length of the tube, converted to a `pint.Quantity`.
    - `material`: The material of the tube.
    - `OD`: The outer diameter of the tube, converted to a `pint.Quantity`.
    - `volume`: The volume of the tube, as determined from the length and inner diameter, converted to a `pint.Quantity`.

    Raises:
        - ValueError: When the outer diameter is less than the inner diameter of the tube.
    """

    def __init__(self, length: str, ID: str, OD: str, material: str):
        """
        See the `Tube` attributes for a description of the arguments.

        ::: tip Note
        The arguments to __init__ are `str`s, not `pint.Quantity`s.
        :::
        """
        self.length = ureg.parse_expression(length)
        self.ID = ureg.parse_expression(ID)
        self.OD = ureg.parse_expression(OD)

        # check to make sure units are valid
        for measurement in [self.length, self.ID, self.OD]:
            if measurement.dimensionality != ureg.mm.dimensionality:
                raise ValueError(
                    f"{measurement.units} is an invalid unit of measurement for length."
                )

        # ensure diameters are valid
        if self.OD <= self.ID:
            raise ValueError(
                f"Outer diameter {OD} must be greater than inner diameter {ID}"
            )
        if self.length < self.OD or self.length < self.ID:
            warn(
                f"Tube length ({self.length}) is less than diameter."
                " Make sure that this is not in error."
            )

        self.material = material
        self.volume = pi * ((self.ID / 2) ** 2) * self.length

    def __repr__(self):
        return f"Tube of length {self.length}, ID {self.ID}, OD {self.OD}"
