from pint import UnitRegistry

# unit registry for conversions
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)  # type: ignore
import pkg_resources

__version__ = pkg_resources.get_distribution("mechwolf").version

# to avoid circular import
from .core.apparatus import Apparatus
from .core.protocol import Protocol
from .components import *  # type: ignore
from .core.experiment import Experiment

from . import zoo

# deactivate logging (see https://loguru.readthedocs.io/en/stable/overview.html#suitable-for-scripts-and-libraries)
from loguru import logger

logger.remove()
