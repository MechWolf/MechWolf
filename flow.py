from components import *

from graphviz import Digraph
import networkx as nx
from terminaltables import SingleTable
from pint import UnitRegistry
import json

class Apparatus(object):
	id_counter = 0
	def __init__(self, name=None):
		self.network = []
		self.components = set()
		# if given a name, then name the appartus, else default to a sequential name
		if name is not None:
			self.name = name
		else:
			self.name = "Apparatus_" + str(Apparatus.id_counter)
			Apparatus.id_counter += 1
	
	def add(self, from_component, to_component, tube):
		'''add a connection in the apparatus'''
		assert issubclass(from_component.__class__, Component)
		assert issubclass(to_component.__class__, Component)
		assert issubclass(tube.__class__, Tube)
		
		self.network.append((from_component, to_component, tube))
		self.components.update([from_component, to_component])

	def visualize(self, label=True, node_attr={}, edge_attr={}, graph_attr={}, format="pdf", filename=None):
		'''generate a visualization of the graph of an apparatus'''
		self.compile() # ensure apparatus is valid
		f = Digraph(name=self.name, 
					node_attr=node_attr, 
					edge_attr=edge_attr, 
					graph_attr=graph_attr, 
					format=format, 
					filename=filename)

		# go from left to right adding components and their tubing connections
		f.attr(rankdir='LR')
		f.attr('node', shape='circle')
		for x in self.network:
			f.edge(x[0].name, x[1].name, label=f"Length {x[2].length}\nID {x[2].inner_diameter}\nOD {x[2].outer_diameter}")

		# show the title of the graph
		if label:
			label = label if label != True else self.name
			f.attr(label=label)

		f.view(cleanup=True)

	def summarize(self):
		'''print a summary table of the apppartus'''
		self.compile() # ensure apparatus is valid
		summary = [["Name", "Type", "Address"]] # header rows of components table
		for component in list(self.components):
			component_summary = [component.name, component.__class__.__name__]
			if issubclass(component.__class__, ActiveComponent): # add the address if it has one
				component_summary.append(component.address)
			else:
				component_summary.append("")
			summary.append(component_summary)

		# generate the components table
		table = SingleTable(summary)
		table.title = "Components"
		print(table.table)

		# store and calculate the computed totals for tubing
		total_length = 0 * ureg.mm
		total_volume = 0 * ureg.ml
		for tube in [x[2] for x in self.network]:
			total_length += tube.length
			total_volume += tube.volume

		# summarize the tubing
		summary = [["From", "To", "Length", "Inner Diameter", "Outer Diameter", "Volume", "Temp"]] # header row
		for edge in self.network:
			summary.append([edge[0].name, 
							edge[1].name, 
							round(edge[2].length, 4), 
							round(edge[2].inner_diameter, 4), 
							round(edge[2].outer_diameter, 4), 
							round(edge[2].volume.to("ml"), 4)])
			if edge[2].temp is not None:
				summary[-1].append(round(edge[2].temp, 4))
			else:
				summary[-1].append(None)
		summary.append(["", "Total", round(total_length, 4), "n/a", "n/a", round(total_volume.to("ml"), 4), "n/a"]) # footer row

		# generate the tubing table
		table = SingleTable(summary)
		table.title = "Tubing"
		table.inner_footing_row_border = "True"
		print(table.table)	

	def __repr__(self):
		return self.name	

	def compile(self):
		'''make sure that the apparatus is valid'''
		G = nx.Graph() # convert the network to an undirected NetworkX graph
		G.add_edges_from([(x[0], x[1]) for x in self.network])
		if not nx.is_connected(G): # make sure that all of the components are connected
			raise ValueError("Unable to compile: not all components connected")

		# make sure that each valve only has one output and that its mapping is valid
		for valve in list(set([x[0] for x in self.network if issubclass(x[0].__class__, Valve)])):
			for name in valve.mapping.keys():
				if name not in valve.used_names:
					raise ValueError(f"Invalid mapping for Valve {valve}. No component named {name} exists.")
			if len([x for x in self.network if x[0] == valve]) != 1:
				raise ValueError(f"Valve {valve} has multiple outputs.")

class Protocol(object):
	def __init__(self, apparatus, duration=None, name=None):
		assert type(apparatus) == Apparatus
		self.apparatus = apparatus
		self.apparatus.compile() # ensure apparatus is valid
		self.procedures = []
		self.continuous_procedures = []
		self.name = name

		# check duration, if given
		if duration is not None:
			duration = ureg.parse_expression(duration)
			if duration.dimensionality != ureg.hours.dimensionality:
				raise ValueError("Incorrect dimensionality for duration.")
		self.duration = duration

	def _is_valid_to_add(self, component, **kwargs):
		# make sure that the component being added to the protocol is part of the apparatus
		if component not in self.apparatus.components:
			raise ValueError(f"{component} is not a component of {self.apparatus.name}")

		# check that the keyword is a valid attribute of the component
		if not component.is_valid_attribute(**kwargs):
			raise ValueError(f"Invalid attributes present for {component.name}.")

		return True
		
	def add(self, start_time, stop_time, component, **kwargs):
		'''add a procedure to the protocol for an apparatus'''
		# make sure the component is valid to add
		if self._is_valid_to_add(component, **kwargs):
			start_time, stop_time = ureg.parse_expression(start_time), ureg.parse_expression(stop_time)

		# ensure that the start time is before the stop time
		if start_time > stop_time:
			raise ValueError("Start time must be less than or equal to stop time.")

		if self.duration is not None and stop_time > self.duration:
			raise ValueError(f"Procedure cannot end after {self.duration} (the duration of the experiment)")

		self.procedures.append((start_time, stop_time, component, kwargs))

	def continuous(self, component, **kwargs):
		'''add a component that be continuously active for the entire duration of the protocol'''
		if not self.duration:
			raise ValueError("Must set experiment duration.")
		if self._is_valid_to_add(component, **kwargs):
			self.continuous_procedures.append((component, kwargs))

	def compile(self):

		# make sure all active components are activated, raising warning if not
		for component in [x for x in self.apparatus.components if issubclass(x.__class__, ActiveComponent)]:
			if component not in [x[2] for x in self.procedures] and component not in [x[0] for x in self.continuous_procedures]:
				raise Warning("Not all active components activated.")
