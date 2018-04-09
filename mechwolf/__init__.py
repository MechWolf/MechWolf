from colorama import init
from pint import UnitRegistry

# unit registry for conversions
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)

RESOLVER_URL = "https://01l52kldqc.execute-api.us-east-1.amazonaws.com/dev/"
'''The url of the MechWolf resolver.'''

# initialize colored printing
init(autoreset=True)

# to avoid circular import
from .mechwolf import Apparatus, Protocol
from .components import *
from .validate_component import validate_component
from .generate_security_key import generate_security_key
