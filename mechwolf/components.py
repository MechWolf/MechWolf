from math import pi
import re
from warnings import warn
from abc import ABCMeta, abstractmethod
import time
import serial

from pint import UnitRegistry
from cirpy import Molecule
from colorama import init, Fore, Back, Style
from terminaltables import SingleTable

# initialize colored printing
init(autoreset=True)

# unit registry for unit conversion and parsing
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)

class Component(object):
    """One of the individial, irreducible parts of a flow chemistry setup.

    All components in an :class:`flow.Apparatus` must be of type :class:`Component`. However, it is unlikely that a user
    will directly instantiate a :class:`Component`.

    Attributes:
        Name (str, optional): the name of the component.
    """
    _id_counter = 0
    used_names = set()

    def __init__(self, name=None):
        # name the object, either sequentially or with a given name
        if name is None:
            self.name = self.__class__.__name__ + "_" + str(self.__class__._id_counter)
            self.__class__._id_counter += 1
        elif name not in self.__class__.used_names:
            self.name = name
        else:
            raise ValueError(Fore.RED + f"Cannot have two components with the name {name}.")
        self.__class__.used_names.add(self.name)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

class ActiveComponent(Component, metaclass=ABCMeta):
    """A connected, controllable component.

    All components beind manipulated in an :class:`flow.Protocol` must be of type :class:`ActiveComponent`.

    Note:
        Users should not directly instantiate an :class:`ActiveComponent` for use in a :class:`flow.Protocol` becuase
        it is not a functioning laboratory instrument.

     Attributes:
        Name (str, optional): the name of the component.

    """
    _id_counter = 0

    def __init__(self, name=None):
        if name is None:
            raise ValueError(Fore.RED + "No name given for ActiveComponent. Specify the name of the component by adding name=\"[name of component]\" to the line that generated this error.")
        super().__init__(name=name)

    def update_from_params(self, params):
        '''Updates the attributes of the object from a dict.

        Args:
            params (dict): A dict whose keys are the strings of attribute names and values are the new values of the attribute.

        '''
        for key, value in params.items():
            setattr(self, key, value)

    @abstractmethod
    def base_state():
        '''A placeholder method for the base state of the component.

        All subclasses of ActiveComponent must implement a function that returns a dict of its base state.
        At the end of a protocol, the component will return to this state.

        Note:
            The dict that :meth:`ActiveComponent.base_state` returns, must have values which can be parsed into compatible
            units of the object's attributes, if applicable. For example, :meth:`Pump.base_state` returns
            ``{"rate": "0 ml/min"}``.
        '''
        # pass

class Pump(ActiveComponent):
    '''A pumping device whose primary attribute is that it moves fluid.

    Note:
        Users should not directly instantiate an :class:`Pump` for use in a :class:`flow.Protocol` becuase
        it is not a functioning laboratory instrument

    Attributes:
        rate (str)
    '''
    def __init__(self, name=None):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")

    def base_state(self):
        '''Returns the base state of a pump'''
        return dict(rate="0 ml/min")

class VarianPump(Pump):
    '''A Varian pump.
    '''
    def __init__(self, name=None, max_rate=0):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self.max_rate = max_rate

    def base_state(self):
        '''Returns the base state of a pump'''
        return dict(rate="0 ml/min")

    def update(self):
        print(ureg.parse_expression(self.rate).to(ureg.ml / ureg.min).magnitude / self.max_rate)

class TempControl(ActiveComponent):
    def __init__(self, internal_tubing, name=None):
        super().__init__(name=name)
        if type(internal_tubing) != Tube:
            raise TypeError(Fore.RED + "TempControl must have internal_tubing of type Tube.")
        self.temp = ureg.parse_expression("0 degC")
        self.active = False

    def base_state(self):
        return dict(temp="0 degC", active=False)

class Sensor(ActiveComponent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.active = False

    def base_state(self):
        return dict(active=False)

class Tube(object):
    def __init__(self, length, ID, OD, material, temp=None):
        self.length = ureg.parse_expression(length)
        self.ID = ureg.parse_expression(ID)
        self.OD = ureg.parse_expression(OD)

        # ensure diameters are valid
        if self.OD <= self.ID:
            raise ValueError(Fore.RED + f"Outer diameter {OD} must be greater than inner diameter {ID}")
        if self.length < self.OD or self.length < self.ID:
            warn(Fore.YELLOW + f"Tube length ({self.length}) is less than diameter. Make sure that this is not in error.")

        self.material = material

        if temp:
            self.temp = ureg.parse_expression(temp)
        else:
            self.temp = None
        self.volume = (pi * ((self.ID / 2)**2) * self.length)

        # check to make sure units are valid
        for measurement in [self.length, self.ID, self.OD]:
            if measurement.dimensionality != ureg.mm.dimensionality:
                raise ValueError(Fore.RED + f"{measurement.dimensionality} is an invalid unit of measurement for {measurement}. Must be a {ureg.mm.dimensionality}.")
        if self.temp is not None and self.temp.dimensionality != ureg.degC.dimensionality:
            raise ValueError(Fore.RED + "Invalid temperature unit. Use \"degC\", \"degF\" or \"degK\".")

    def __repr__(self):
        return f"Tube of length {self.length}, ID {self.OD}, OD {self.OD}"

class Valve(ActiveComponent, metaclass=ABCMeta):
    def __init__(self, mapping={}, name=None):
        super().__init__(name=name)
        self.mapping = mapping
        self.setting = 1

    def base_state(self):
        # an arbitrary state
        return dict(setting=list(self.mapping.items())[0][1])

    def update(self):
        print(f"Setting at {self.setting}")

class ViciValve(Valve):
    '''Controls a VICI Valco Valve'''

    def __init__(self, mapping={}, name=None, serial_port=None, positions=10):
        super().__init__(mapping=mapping, name=name)

        self.serial_port = serial_port
        self.positions = positions

    def __enter__(self):
        self.ser = serial.Serial(self.serial_port, 115200, parity=serial.PARITY_NONE, stopbits=1, timeout=0.1)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()
        return self

    def get_position(self):
        self.ser.write(b'CP\r')
        response = self.ser.readline()
        if response:
            position = int(response[2:4]) # Response is in the form 'CPXX\r'
            return position
        else:
            return False

    def set_position(self, position):
        if not position > 0 and position <= self.positions:
            return False
        else:
            message = f'GO{position}\r'
            self.ser.write(message.encode())
            return True

    def update(self):
        if self.get_position() != self.setting:
            self.set_position(self.setting)

class Vessel(Component):
    def __init__(self, description, name=None, resolve=True, warnings=True):
        super().__init__(name=name)
        if resolve:
            hits = list(re.findall(r"`(.+?)`", description))
            try: # in case the resolver is down, don't break
                for hit in hits:
                    M = Molecule(hit)
                    description = description.replace(f"`{hit}`", f"{hit} ({M.iupac_name})")

                    if warnings:
                        table = SingleTable([
                            ["IUPAC Name", M.iupac_name],
                            ["CAS", M.cas],
                            ["Formula", M.formula]])
                        table.title = "Resolved: " + hit
                        table.inner_heading_row_border = False
                        print(table.table)
            except:
                warn(Fore.YELLOW + "Resolver failed. Continuing without resolving.")

        self.description = description

class Test(ActiveComponent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.active = False

    def base_state(self):
        return dict(active=False)

    def update(self):
        if self.active:
            print("Active!")
        else:
            print("Inactive.")
        return self.__dict__
