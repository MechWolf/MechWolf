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
from .components import *
from .experiment import Experiment

import stackprinter

# set the color coding based on whether in use in terminal
try:
    get_ipython()
    stackprinter.set_excepthook(style="lightbg")
except NameError:
    stackprinter.set_excepthook(style="darkbg2")

import warnings
from loguru import logger

showwarning_ = warnings.showwarning


def showwarning(message, *args, **kwargs):
    logger.warning(message)
    # showwarning_(message, *args, **kwargs)


warnings.showwarning = showwarning

import sys

logger.remove()
logger.add(sys.stdout, level="TRACE")
