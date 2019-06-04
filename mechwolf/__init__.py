from pint import UnitRegistry
from blessings import Terminal

# unit registry for conversions
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)

# initialize colored printing
term = Terminal()

__version__ = "0.0.1"

# to avoid circular import
from .apparatus import Apparatus
from .protocol import Protocol
from .execute import execute, jupyter_execute, Experiment
from .components import *
from .validate_component import validate_component

import logging

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

import stackprinter

stackprinter.set_excepthook(style="lightbg")
