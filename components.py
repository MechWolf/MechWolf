from math import pi
from pint import UnitRegistry
from warnings import warn
from abc import ABCMeta, abstractmethod
from cirpy import Molecule

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
            raise ValueError(f"Cannot have two components with the name {name}.")
        self.__class__.used_names.add(self.name)

    def __repr__(self):
        return self.name
        
class ActiveComponent(Component, metaclass=ABCMeta):
    """A connected, controllable component."""
    id_counter = 0

    def __init__(self, name=None):
        if name is None:
            raise ValueError("No name given for ActiveComponent. Specify the name of the component by adding name=\"[name of component]\" to the line that generated this error.")
        super().__init__(name=name)

    @abstractmethod
    def base_state():
        '''All subclasses of ActiveComponent must implement a function that returns a dictionary of its base state'''
        return

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
            raise TypeError("TempControl must have internal_tubing of type Tube.")
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
        if outer_diameter <= inner_diameter:
            raise ValueError("Outer diameter must be greater than inner diameter")
        if length <= outer_diameter or length <= inner_diameter:
            warn("Tube length is less than diameter. Make sure that this is not in error.")
        
        if type(material) != str:
            raise TypeError("Material must be a string")
        self.material = material

        if temp:
            self.temp = ureg.parse_expression(temp)
        else:
            self.temp = None
        self.volume = (pi * ((self.inner_diameter / 2)**2) * self.length)

        # check to make sure units are valid
        for measurement in [self.length, self.inner_diameter, self.outer_diameter]:
            if measurement.dimensionality != ureg.mm.dimensionality:
                raise ValueError(f"{measurement.dimensionality} is an invalid unit of measurement for {measurement}. Must be a {ureg.mm.dimensionality}.")
        if self.temp is not None and self.temp.dimensionality != ureg.degC.dimensionality:
            raise ValueError("Invalid temperature unit. Use \"degC\", \"degF\" or \"degK\".")
    
    def __repr__(self):
        return f"Tube of length {self.length}, ID {self.outer_diameter}, OD {self.outer_diameter}"

class Valve(ActiveComponent):
    def __init__(self, mapping, name=None):
        super().__init__(name=name)
        self.mapping = mapping
        self.setting = ""
        assert type(mapping) == dict

    def base_state(self):
        # an arbitrary state
        return dict(setting=list(self.mapping.items())[0][1])

class Vessel(Component):
    def __init__(self, solution_volume, solvent, solute_mass, solute, name=None):
        super().__init__(name=name)

        self.solution_volume = ureg.parse_expression(solution_volume)
        if self.solution_volume.dimensionality != ureg.ml.dimensionality:
            raise ValueError(f"{self.solution_volume.dimensionality} is an invalid unit of measurement for solution_volume. Must be {ureg.ml.dimensionality}.")

        try:
            self.solvent = Molecule(solvent)
            assert self.solvent is not None
        except:
            self.solvent = solvent

        self.solute_mass = ureg.parse_expression(solute_mass)
        if self.solute_mass.dimensionality != ureg.kg.dimensionality:
            raise ValueError(f"{self.solute_mass.dimensionality} is an invalid unit of measurement for solute_mass. Must be {ureg.kg.dimensionality}.")

        try:
            self.solute = Molecule(solute)
            assert self.solute is not None
        except:
            self.solute = solute
        

