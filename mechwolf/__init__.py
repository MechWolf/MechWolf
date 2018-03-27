from colorama import init
from pint import UnitRegistry

# unit registry for conversions
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)

# initialize colored printing
init(autoreset=True)

# to avoid circular import
from .mechwolf import Apparatus, Protocol
from .components import *
