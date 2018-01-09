from math import pi
from pint import UnitRegistry
from warnings import warn

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
			raise ValueError("Cannot have two components with the same name.")
		self.__class__.used_names.add(self.name)

	def __repr__(self):
		return self.name

	def is_valid_attribute(self, **kwargs):
		return False if kwargs else True # base components have no configurable attributes
		
class ActiveComponent(Component):
	"""A connected, controllable component. Must have an address"""
	id_counter = 0

	def __init__(self, address, name):
		super().__init__(name=name)
		self.address = address

	def __repr__(self):
		return self.name

	def is_valid_attribute(self, **kwargs):
		return False if kwargs else True # active components have no configurable attributes by themselves

class Pump(ActiveComponent):
	id_counter = 0

	def __init__(self, address, name=None):
		super().__init__(address, name=name)

	def is_valid_attribute(self, **kwargs):
		try:
			assert ureg.parse_expression(kwargs["rate"]).dimensionality == ureg.parse_expression("1 ml/min").dimensionality
		except KeyError:
			raise(ValueError(f"Invalid attribute for {self.__class__.__name__}. Please provide \"rate\"."))
		except (AssertionError, AttributeError):
			raise ValueError("Invalid dimensionality. Rate must be volume/time.")
		return True

class Sensor(ActiveComponent):
	id_counter = 0

	def __init__(self, address, name=None):
		super().__init__(address, name=name)

	def is_valid_attribute(self, **kwargs):
		try:
			assert type(kwargs["active"]) == bool
		except AssertionError:
			raise ValueError("Invalid sensor activation setting. Must be boolean.")
		return True
		

class Tube(object):
	def __init__(self, length, inner_diameter, outer_diameter, material=None, temp=None):
		self.length = ureg.parse_expression(length)
		self.inner_diameter = ureg.parse_expression(inner_diameter)
		self.outer_diameter = ureg.parse_expression(outer_diameter)
		
		# ensure diameters are valid
		if outer_diameter <= inner_diameter:
			raise ValueError("Outer diameter must be greater than inner diameter")
		if length <= outer_diameter or length <= inner_diameter:
			warn("Tube length is less than diameter. Make sure that this is not in error.")
			
		self.material = material

		if temp:
			self.temp = ureg.parse_expression(temp)
		else:
			self.temp = None
		self.volume = (pi * ((self.inner_diameter / 2)**2) * self.length)

		# check to make sure units are valid
		for measurement in [self.length, self.inner_diameter, self.outer_diameter]:
			if measurement.dimensionality != ureg.mm.dimensionality:
				raise ValueError(f"Invalid unit of measurement for {measurement}. Must be a length.")
		if self.temp is not None and self.temp.dimensionality != ureg.degC.dimensionality:
			raise ValueError("Invalid temperature unit. Use \"degC\", \"degF\" or \"degK\".")
	
	def __repr__(self):
		return f"Tube of length {self.length}, ID {self.outer_diameter}, OD {self.outer_diameter}"

class Valve(ActiveComponent):
	id_counter = 0

	def __init__(self, address, mapping, name=None):
		super().__init__(address, name=name)
		self.mapping = mapping
		assert type(mapping) == dict

	def is_valid_attribute(self, **kwargs):
		try:
			assert type(self.mapping[kwargs["setting"]]) == str
		except KeyError:
			raise ValueError("Invalid valve setting.")
		except AssertionError:
			raise ValueError("Valve setting must be a string.")
		return True
