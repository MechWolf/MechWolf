from components import *
from connection import Connection, DeviceExecutor

from graphviz import Digraph
import networkx as nx
from terminaltables import SingleTable
from pint import UnitRegistry
import plotly as py
import plotly.figure_factory as ff
from plotly.colors import DEFAULT_PLOTLY_COLORS as colors

from copy import deepcopy
from datetime import datetime, timedelta
from pprint import pprint
import time
import json
from warnings import warn
from datetime import datetime, timedelta

class Apparatus(object):
    id_counter = 0

    def __init__(self, name=None):
        self.network = []
        self.components = set()
        # if given a name, then name the apparatus, else default to a sequential name
        if name is not None:
            self.name = name
        else:
            self.name = "Apparatus_" + str(Apparatus.id_counter)
            Apparatus.id_counter += 1

    def __repr__(self):
        return self.name  
    
    def add(self, from_component, to_component, tube):
        '''add a connection in the apparatus'''
        assert issubclass(from_component.__class__, Component)
        assert issubclass(to_component.__class__, Component)
        assert issubclass(tube.__class__, Tube)
        
        self.network.append((from_component, to_component, tube))
        self.components.update([from_component, to_component])

    def visualize(self, title=True, label_tubes=False, node_attr={}, edge_attr={}, graph_attr=dict(splines="ortho",  nodesep="1"), format="pdf", filename=None):
        '''generate a visualization of the graph of an apparatus'''
        self.validate() # ensure apparatus is valid
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
            tube_label = f"Length {x[2].length}\nID {x[2].inner_diameter}\nOD {x[2].outer_diameter}" if label_tubes else ""
            f.edge(x[0].name, x[1].name, label=tube_label)

        # show the title of the graph
        if title:
            title = title if title != True else self.name
            f.attr(label=title)

        f.view(cleanup=True)

    def summarize(self):
        '''print a summary table of the apppartus'''
        self.validate() # ensure apparatus is valid
        summary = [["Name", "Type"]] # header rows of components table
        for component in list(self.components):
            summary.append([component.name, component.__class__.__name__])

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
        summary = [["From", "To", "Length", "Inner Diameter", "Outer Diameter", "Volume", "Material", "Temp"]] # header row
        for edge in self.network:
            summary.append([edge[0].name, 
                            edge[1].name, 
                            round(edge[2].length, 4), 
                            round(edge[2].inner_diameter, 4), 
                            round(edge[2].outer_diameter, 4), 
                            round(edge[2].volume.to("ml"), 4),
                            edge[2].material])
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

    def validate(self):
        '''make sure that the apparatus is valid'''
        G = nx.Graph() # convert the network to an undirected NetworkX graph
        G.add_edges_from([(x[0], x[1]) for x in self.network])
        if not nx.is_connected(G): # make sure that all of the components are connected
            raise RuntimeError("Unable to validate: not all components connected")

        # valve checking
        for valve in list(set([x[0] for x in self.network if issubclass(x[0].__class__, Valve)])):
            for name in valve.mapping.keys():
                # ensure that valve's mapping components are part of apparatus
                if name not in valve.used_names:
                    raise RuntimeError(f"Invalid mapping for Valve {valve}. No component named {name} exists.")
            # no more than one output from a valve (might have to change this)
            if len([x for x in self.network if x[0] == valve]) != 1:
                raise RuntimeError(f"Valve {valve} has multiple outputs.")

            # make sure valve's mapping is complete
            non_mapped_components = [x[0] for x in self.network if x[1] == valve and valve.mapping.get(x[0].name) is None]
            if non_mapped_components:
                raise RuntimeError(f"Valve {valve} has incomplete mapping. No mapping for {non_mapped_components}")

        return True

    def description(self):
        '''returns a human readable description of the apparatus'''
        def _description(element):
            '''takes a component and converts it to a string description'''
            if issubclass(element.__class__, Vessel):
                return f"A vessel containing {element.description}"
            elif issubclass(element.__class__, Component):
                return element.__class__.__name__ + " " + element.name
            else:
                raise RuntimeError(f"{element} cannot be described.")

        result = ""

        # iterate over the network and describe the connections
        for element in self.network:
            from_component, to_component, tube = _description(element[0]), _description(element[1]), element[2]
            result += f"{from_component} was connected to {to_component} using {element[2].material} tubing (length {element[2].length}, ID {element[2].inner_diameter}, OD {element[2].outer_diameter}). "

        return result

class Protocol(object):
    id_counter = 0

    def __init__(self, apparatus, duration=None, name=None):
        assert type(apparatus) == Apparatus
        if apparatus.validate(): # ensure apparatus is valid
            self.apparatus = apparatus
        self.procedures = []
        if name is not None:
            self.name = name
        else:
            self.name = "Protocol_" + str(Protocol.id_counter)
            Protocol.id_counter += 1

        # check duration, if given
        if duration not in [None, "auto"]:
            duration = ureg.parse_expression(duration)
            if duration.dimensionality != ureg.hours.dimensionality:
                raise ValueError(f"{duration.dimensionality} is an invalid unit of measurement for duration. Must be {ureg.hours.dimensionality}")
        self.duration = duration

    def _is_valid_to_add(self, component, **kwargs):
        # make sure that the component being added to the protocol is part of the apparatus
        if component not in self.apparatus.components:
            raise ValueError(f"{component} is not a component of {self.apparatus.name}.")

        # check that the keyword is a valid attribute of the component
        if not component.is_valid_attribute(**kwargs):
            raise ValueError(f"Invalid attributes present for {component.name}.")
        
    def add(self, component, start_time="0 seconds", stop_time=None, duration=None, **kwargs):
        '''add a procedure to the protocol for an apparatus'''

        # make sure the component is valid to add
        for kwarg, value in kwargs.items():
            if not hasattr(component, kwarg):
                raise ValueError(f"Invalid attribute {kwarg} for {component}. Valid attributes are {[x for x in vars(component).keys() if x != 'name']}")
            
            if type(component.__dict__[kwarg]) == ureg.Quantity and ureg.parse_expression(value).dimensionality != component.__dict__[kwarg].dimensionality:
                raise ValueError(f"Bad dimensionality of {kwarg} for {component}. Expected dimensionality of {component.__dict__[kwarg].dimensionality} but got {ureg.parse_expression(value).dimensionality}.")
            
            elif type(component.__dict__[kwarg]) != type(value) and type(component.__dict__[kwarg]) != ureg.Quantity:
                raise ValueError(f"Bad type matching. Expected {kwarg} to be {type(component.__dict__[kwarg])} but got {type(value)}")

        if stop_time is not None and duration is not None:
            raise RuntimeError("Must provide one of stop_time and duration, not both.")

        # parse the start time if given
        if isinstance(start_time, timedelta):
            start_time = str(start_time.total_seconds()) + " seconds"
        start_time = ureg.parse_expression(start_time)

        # parse duration if given
        if duration is not None:
            if isinstance(duration, timedelta):
                duration = str(duration.total_seconds()) + " seconds"
            stop_time = start_time + ureg.parse_expression(duration)

        # determine stop time
        if stop_time is None and self.duration is None and duration is None:
            raise RuntimeError("Must specify protocol duration during instantiation in order to omit stop_time. " \
                f"To automatically set duration as end of last procedure in protocol, use duration=\"auto\" when creating {self.name}.")
        elif stop_time is not None:
            if isinstance(stop_time, timedelta):
                stop_time = str(stop_time.total_seconds()) + " seconds"
            if type(stop_time) == str:
                stop_time = ureg.parse_expression(stop_time)

        # perform the mapping for valves
        if issubclass(component.__class__, Valve) and kwargs.get("setting") is not None:
            kwargs["setting"] = component.mapping[kwargs["setting"]]

        # a little magic for temperature controllers
        if issubclass(component.__class__, TempControl):
            if kwargs.get("temp") is not None and kwargs.get("active") is None:
                kwargs["active"] = True
            elif kwargs.get("active") == False and kwargs.get("temp") is None:
                kwargs["temp"] = "0 degC"
            elif kwargs["active"] and kwargs.get("temp") is None:
                raise RuntimeError(f"TempControl {component} is activated but temperature setting is not given. Specify 'temp' in your call to add().")

        # add the procedure to the procedure list
        self.procedures.append(dict(start_time=start_time, stop_time=stop_time, component=component, params=kwargs))

    def compile(self, warnings=True):
        '''compile the protocol into a dict of devices and lists of their procedures'''
        output = {}

        # infer the duration of the protocol
        if self.duration == "auto":
            self.duration = sorted([x["stop_time"] for x in self.procedures], key=lambda z: z.to_base_units().magnitude if type(z) == ureg.Quantity else 0)
            if all([x == None for x in self.duration]):
                raise RuntimeError("Unable to automatically infer duration of protocol. Must define stop_time for at least one procedure to use duration=\"auto\".")
            self.duration = self.duration[-1]

        
        for component in [x for x in self.apparatus.components if issubclass(x.__class__, ActiveComponent)]:
            # make sure all active components are activated, raising warning if not
            if component not in [x["component"] for x in self.procedures]:
                if warnings: warn(f"{component} is an active component but was not used in this procedure. If this is intentional, ignore this warning. To suppress this warning, use warnings=False.")

            # determine the procedures for each component
            component_procedures = sorted([x for x in self.procedures if x["component"] == component], key=lambda x: x["start_time"])

            # skip compilation of components with no procedures added
            if not len(component_procedures):
                continue

            # check for conflicting continuous procedures
            if len([x for x in component_procedures if x["start_time"] is None and x["stop_time"] is None]) > 1:
                raise RuntimeError((f"{component} cannot have two procedures for the entire duration of the protocol. " 
                    "If each procedure defines a different attribute to be set for the entire duration, combine them into one call to add(). "  
                    "Otherwise, reduce ambiguity by defining start and stop times for each procedure."))

            for i, procedure in enumerate(component_procedures):
                # ensure that the start time is before the stop time if given
                if procedure["stop_time"] is not None and procedure["start_time"] > procedure["stop_time"]:
                    raise RuntimeError("Start time must be less than or equal to stop time.")

                # make sure that the start time isn't outside the duration
                if self.duration is not None and procedure["start_time"] is not None and procedure["start_time"] > self.duration:
                    raise ValueError(f"Procedure cannot start at {procedure['start_time']}, which is outside the duration of the experiment ({self.duration}).")

                # make sure that the end time isn't outside the duration
                if self.duration is not None and procedure["stop_time"] is not None and procedure["stop_time"] > self.duration:
                    raise ValueError(f"Procedure cannot end at {procedure['stop_time']}, which is outside the duration of the experiment ({self.duration}).")
                
                # automatically infer start and stop times
                try:
                    if component_procedures[i+1]["start_time"] == ureg.parse_expression("0 seconds"):
                        raise RuntimeError(f"Ambiguous start time for {procedure['component']}.")
                    elif component_procedures[i+1]["start_time"] is not None and procedure["stop_time"] is None:
                        if warnings: warn(f"Automatically inferring start time for {procedure['component']} as beginning of {procedure['component']}'s next procedure. To suppress this warning, use warnings=False.")
                        procedure["stop_time"] = component_procedures[i+1]["start_time"]
                except IndexError:
                    if procedure["stop_time"] is None:
                        if warnings: warn(f"Automatically inferring stop_time for {procedure['component']} as the end of the protocol. To override, provide stop_time in your call to add(). To suppress this warning, use warnings=False.")
                        procedure["stop_time"] = self.duration 

            # give the component instructions at all times
            compiled = []
            for i, procedure in enumerate(component_procedures):
                compiled.append(dict(time=procedure["start_time"], params=procedure["params"]))
                
                # if the procedure is over at the same time as the next procedure begins, do go back to the base state
                try:
                    if component_procedures[i+1]["start_time"] == procedure["stop_time"]:
                        continue
                except IndexError:
                    pass

                # otherwise, go back to base state
                compiled.append(dict(time=procedure["stop_time"], params=component.base_state()))

            output[component] = compiled
        return output

    def json(self, warnings=True):
        '''convert compiled protocol to json'''
        compiled = deepcopy(self.compile(warnings=warnings))
        for item in compiled.items():
            for procedure in item[1]:
                procedure["time"] = procedure["time"].to_timedelta().total_seconds()
        compiled = {str(k): v for (k, v) in compiled.items()}
        return json.dumps(compiled, indent=4, sort_keys=True)

    def visualize(self, warnings=True):
        '''convert protocol to df for plotting'''
        df = []
        for component, procedures in self.compile(warnings=warnings).items():
            for procedure in procedures:
                df.append(dict(
                    Task=str(component),
                    Start=str(datetime(2000, 1, 1) + procedure["start_time"].to_timedelta()),
                    Finish=str(datetime(2000, 1, 1) + procedure["stop_time"].to_timedelta()),
                    Resource=str(procedure["params"])))
        df.sort(key=lambda x: x["Task"])

        # ensure that color coding keeps color consistent for params
        colors_dict = {}
        color_idx = 0
        for params in list(set([str(x["params"]) for x in self.procedures])):
            colors_dict[params] = colors[color_idx % len(colors)]
            color_idx += 1

        # create the graph
        fig = ff.create_gantt(df, group_tasks=True, colors=colors_dict, index_col='Resource', showgrid_x=True, title=self.name)

        # add the hovertext
        for i in range(len(fig["data"])):
            fig["data"][i].update(text=df[i]["Resource"], hoverinfo="text")
        fig['layout'].update(margin=dict(l=110))

        # plot it
        py.offline.plot(fig, filename=f'{self.name}.html')

    def execute(self):
        c = Connection()
        c.connect()
        e = DeviceExecutor(c)

        tasks = []

        compiled = json.loads(self.json()) # i hate this

        pprint(compiled)
        for device in list(self.apparatus.components):
            if issubclass(device.__class__, ActiveComponent):
                tasks.extend([e.submit(device.address, procedure) for procedure in compiled[device.name]])
        
        print(tasks)

        while not all([task._state == "RECEIVED" for task in tasks]):
            time.sleep(3)
            e.resend_all()

        for device in list(self.apparatus.components):
            e.submit(device.name,{'run':True})
        return tasks

