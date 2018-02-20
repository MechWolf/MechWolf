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
import Pyro4

# initialize colored printing
init(autoreset=True)

# unit registry for unit conversion and parsing
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)

class Component(object):
    """One of the individial, irreducible parts of a flow chemistry setup"""
    id_counter = 0
    used_names = set()

    def __init__(self, name=None):
        # name the object, either sequentially or with a given name
        if name is None:
            self.name = self.__class__.__name__ + "_" + str(self.__class__.id_counter) 
            self.__class__.id_counter += 1
        elif name not in self.__class__.used_names:
            self.name = name
        else:
            raise ValueError(Fore.RED + f"Cannot have two components with the name {name}.")
        self.__class__.used_names.add(self.name)

    def __repr__(self):
        return self.name

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")    
class ActiveComponent(Component, metaclass=ABCMeta):
    """A connected, controllable component."""
    id_counter = 0

    def __init__(self, name=None):
        if name is None:
            raise ValueError(Fore.RED + "No name given for ActiveComponent. Specify the name of the component by adding name=\"[name of component]\" to the line that generated this error.")
        super().__init__(name=name)

    def update_from_params(self, params):
        for key, value in params.items():
            setattr(self, key, value)

    @abstractmethod
    def base_state():
        '''All subclasses of ActiveComponent must implement a function that returns a dictionary of its base state'''
        pass

class Pump(ActiveComponent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")

    def base_state(self):
        return dict(rate="0 ml/min")
 
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
    def __init__(self, length, inner_diameter, outer_diameter, material, temp=None):
        self.length = ureg.parse_expression(length)
        self.inner_diameter = ureg.parse_expression(inner_diameter)
        self.outer_diameter = ureg.parse_expression(outer_diameter)
        
        # ensure diameters are valid
        if self.outer_diameter <= self.inner_diameter:
            raise ValueError(Fore.RED + f"Outer diameter {outer_diameter} must be greater than inner diameter {inner_diameter}")
        if self.length < self.outer_diameter or self.length < self.inner_diameter:
            warn(Fore.YELLOW + f"Tube length ({self.length}) is less than diameter. Make sure that this is not in error.")
        
        self.material = material

        if temp:
            self.temp = ureg.parse_expression(temp)
        else:
            self.temp = None
        self.volume = (pi * ((self.inner_diameter / 2)**2) * self.length)

        # check to make sure units are valid
        for measurement in [self.length, self.inner_diameter, self.outer_diameter]:
            if measurement.dimensionality != ureg.mm.dimensionality:
                raise ValueError(Fore.RED + f"{measurement.dimensionality} is an invalid unit of measurement for {measurement}. Must be a {ureg.mm.dimensionality}.")
        if self.temp is not None and self.temp.dimensionality != ureg.degC.dimensionality:
            raise ValueError(Fore.RED + "Invalid temperature unit. Use \"degC\", \"degF\" or \"degK\".")
    
    def __repr__(self):
        return f"Tube of length {self.length}, ID {self.outer_diameter}, OD {self.outer_diameter}"

class Valve(ActiveComponent, metaclass=ABCMeta):
    def __init__(self, mapping={}, name=None):
        super().__init__(name=name)
        self.mapping = mapping
        self.setting = 0

    def base_state(self):
        # an arbitrary state
        return dict(setting=list(self.mapping.items())[0][1])

class ViciValve(Valve):
    '''Controls a VICI Valco Valve'''

    def __init__(self, mapping=None, name=None, serial_port=None, positions=10):
        super().__init__(mapping=mapping, name=name)
        self.mapping = mapping
        self.setting = None

        self.serial_port = serial_port
        self.positions = positions

    def __enter__(self):
        self.ser = serial.Serial(self.serial_port, 115200, parity=serial.PARITY_NONE, stopbits=1, timeout=0.1)
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()
        return self  
        
    # def start(self):
    #     self.ser = serial.Serial(self.serial_port, 115200, parity=serial.PARITY_NONE, stopbits=1, timeout=0.1)

    # def stop(self):
    #     self.ser.close()

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


class Vessel(Component):
    def __init__(self, description, name=None, resolve=True, warnings=True):
        super().__init__(name=name)
        if resolve:
            hits = list(re.findall(r"`(.+?)`", description))
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

        self.description = description

class Test(ActiveComponent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.active = False 

    def base_state(self):
        return dict(active=False)

    def update(self):
        if self.active:
            print("Side effect!")
        return self.__dict__

