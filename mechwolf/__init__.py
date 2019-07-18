from pint import UnitRegistry

# unit registry for conversions
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)  # type: ignore

__version__ = "0.0.1"

# to avoid circular import
from .core.apparatus import Apparatus
from .core.protocol import Protocol
from .components import *  # type: ignore
from .core.experiment import Experiment

# deactivate logging (see https://loguru.readthedocs.io/en/stable/overview.html#suitable-for-scripts-and-libraries)
from loguru import logger

logger.remove()
