from math import pi
from warnings import warn

from . import term, ureg


class Tube(object):
    """A tube.

    Attributes:
        length (str): The length of the tube. Converted to a Quantity.
        ID (str): The inner diameter of the tube. Converted to a Quantity.
        OD (str): The outer diameter of the tube. Converted to a Quantity.
        Volume (Quantity): The volume of the tube, as determined from the length and inner diameter.
        material (str): The material of the tube.

    Raises:
        ValueError: When the outer diameter is less than the inner diameter of the tube.
    """

    def __init__(self, length, ID, OD, material):
        self.length = ureg.parse_expression(length)
        self.ID = ureg.parse_expression(ID)
        self.OD = ureg.parse_expression(OD)

        # check to make sure units are valid
        for measurement in [self.length, self.ID, self.OD]:
            if measurement.dimensionality != ureg.mm.dimensionality:
                raise ValueError(
                    term.red(
                        f"{measurement.dimensionality} is an invalid unit of measurement for {measurement}. Must be a {ureg.mm.dimensionality}."
                    )
                )

        # ensure diameters are valid
        if self.OD <= self.ID:
            raise ValueError(
                term.red(
                    f"Outer diameter {OD} must be greater than inner diameter {ID}"
                )
            )
        if self.length < self.OD or self.length < self.ID:
            warn(
                term.yellow(
                    f"Tube length ({self.length}) is less than diameter. Make sure that this is not in error."
                )
            )

        self.material = material
        self.volume = pi * ((self.ID / 2) ** 2) * self.length

    def __repr__(self):
        return f"Tube of length {self.length}, ID {self.ID}, OD {self.OD}"
