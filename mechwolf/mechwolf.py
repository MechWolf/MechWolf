from copy import deepcopy
from datetime import datetime, timedelta
import time
import json
import yaml
from warnings import warn
import sys
import urllib3
import tempfile
import webbrowser

import networkx as nx
from terminaltables import SingleTable
from colorama import Fore, init
import requests
from click import prompt, confirm
import itsdangerous
import keyring

# If visualization extras are available, import them
try:
    from graphviz import Digraph
    from jinja2 import Environment, PackageLoader, select_autoescape
except ImportError:
    pass

from . import ureg, RESOLVER_URL
from .components import *
from .validate_component import validate_component

# initialize colored printing
init(autoreset=True)

# ignore warning when submitting to self signed certificate
urllib3.disable_warnings()

class Apparatus(object):
    '''A unique network of components.

    Note:
        The same components may be organized into multiple distinct apparatuses, depending on the connections between them.

    Attributes:
        network (list): A list of tuples in the form (from_component, to_component, tube) describing the configuration
            of the apparatus.
        components (set): The components that make up the apparatus.
        name (str): The name of the apparatus. Defaults to "Apparatus_X" where *X* is apparatus count.
    '''
    _id_counter = 0

    def __init__(self, name=None):
        self.network = []
        self.components = set()
        # if given a name, then name the apparatus, else default to a sequential name
        if name is not None:
            self.name = name
        else:
            self.name = "Apparatus_" + str(Apparatus._id_counter)
            Apparatus._id_counter += 1

    def __repr__(self):
        return self.name

    def _add_single(self, from_component, to_component, tube):
        '''Adds a single connection to the apparatus.

        For args, see add().
        '''
        if not issubclass(from_component.__class__, Component):
            raise ValueError(Fore.RED + "From component must be a subclass of Component")
        if not issubclass(to_component.__class__, Component):
            raise ValueError(Fore.RED + "To component must be a subclass of Component")
        if not issubclass(tube.__class__, Tube):
            raise ValueError(Fore.RED + "Tube must be an instance of Tube")

        self.network.append((from_component, to_component, tube))
        self.components.update([from_component, to_component])

    def add(self, from_component, to_component, tube):
        '''Adds connections to the apparatus.

        Args:
            from_component (Component or Iterable): The :class:`~mechwolf.components.component.Component` from which the flow is originating. If an iterable, all items in the iterable will be connected to the same component.
            to_component (Component): The :class:`~mechwolf.components.component.Component` where the flow is going.
            tube (Tube): The :class:`~mechwolf.components.tube.Tube` that connects the components.

        Raises:
            ValueError: When the connection being added is invalid.
        '''

        try:
            iter(from_component)
        except TypeError:
            from_component = [from_component]

        for component in from_component:
            self._add_single(component, to_component, tube)

    def visualize(self, title=True, label_tubes=False, node_attr={}, edge_attr={}, graph_attr=dict(splines="ortho", nodesep="1"), file_format="pdf", filename=None):
        '''Generates a visualization of the graph of an apparatus.

        For full list of acceptable Graphviz attributes for see `the
        graphviz.org docs <http://www.graphviz.org/doc/info/attrs.html>`_ and
        `its Python API's docs
        <http://graphviz.readthedocs.io/en/stable/manual.html#attributes>`_.

        Args:
            title (bool, optional): Whether to show the title in the output. Defaults to True.
            label_tubes (bool, optional): Whether to label the tubes between components with the length, inner diameter,
                and outer diameter.
            node_attr (dict, optional): Controls the appearance of the nodes of the graph. Must be of the form
                {"attribute": "value"}.
            edge_attr (dict, optional): Controls the appearance of the edges of the graph. Must be of the form
                {"attribute": "value"}.
            graph_attr (dict, optional): Controls the appearance of the graph. Must be of the form
                {"attribute": "value"}. Defaults to orthogonal splines and a node separation of 1.
            file_format (str, optional): The output format of the graph, either "pdf" or "png". Defaults to "pdf".
            filename (str, optional): The name of the output file. Defaults to the name of the apparatus.

        Raises:
            ImportError: When the visualization package is not installed.
        '''

        if "graphviz" not in sys.modules:
            raise ImportError(Fore.RED + "Visualization package not installed. Install mechwolf with the [vis] extra enabled.")

        self.validate() # ensure apparatus is valid
        f = Digraph(name=self.name,
                    node_attr=node_attr,
                    edge_attr=edge_attr,
                    graph_attr=graph_attr,
                    format=file_format,
                    filename=filename)

        # go from left to right adding components and their tubing connections
        f.attr(rankdir='LR')
        f.attr('node', shape='box')
        for x in self.network:
            tube_label = f"Length {x[2].length}\nID {x[2].ID}\nOD {x[2].OD}" if label_tubes else ""
            f.edge(x[0].name, x[1].name, label=tube_label)

        # show the title of the graph
        if title:
            title = title if not title else self.name
            f.attr(label=title)

        f.view(cleanup=True)

    def summarize(self):
        '''Prints a summary table of the apparatus.'''
        # create a components table
        summary = [["Name", "Type"]] # header rows of components table
        for component in list(self.components):
            if not isinstance(component, Vessel):
                summary.append([component.name, component.__class__.__name__])
            else:
                # we want to know what's actually in the vessel
                summary.append([component.description, component.__class__.__name__])

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
        summary = [["From", "To", "Length", "Inner Diameter", "Outer Diameter", "Volume", "Material"]] # header row
        for edge in self.network:
            summary.append([edge[0].name,
                            edge[1].name,
                            round(edge[2].length, 4),
                            round(edge[2].ID, 4),
                            round(edge[2].OD, 4),
                            round(edge[2].volume.to("ml"), 4),
                            edge[2].material])
        summary.append(["", "Total", round(total_length, 4), "n/a", "n/a", round(total_volume.to("ml"), 4), "n/a"]) # footer row

        # generate the tubing table
        table = SingleTable(summary)
        table.title = "Tubing"
        table.inner_footing_row_border = "True"
        print(table.table)

    def validate(self):
        '''Ensures that the apparatus is valid.

        Note:
            Calling this function yourself is likely unnecessary because the :class:`Protocol` class calls it upon
            instantiation.

        Returns:
            bool: True if valid.

        Raises:
            RuntimeError: If the protocol is invalid.
        '''
        G = nx.Graph() # convert the network to an undirected NetworkX graph
        G.add_edges_from([(x[0], x[1]) for x in self.network])
        if not nx.is_connected(G): # make sure that all of the components are connected
            raise RuntimeError(Fore.RED + "Unable to validate: not all components connected")

        # valve checking
        for valve in list(set([x[0] for x in self.network if issubclass(x[0].__class__, Valve)])):
            for name in valve.mapping.keys():
                # ensure that valve's mapping components are part of apparatus
                if name not in [x.name for x in list(self.components)]:
                    raise RuntimeError(Fore.RED + f"Invalid mapping for Valve {valve}. No component named {name} exists.")
            # no more than one output from a valve (might have to change this)
            if len([x for x in self.network if x[0] == valve]) != 1:
                raise RuntimeError(Fore.RED + f"Valve {valve} has multiple outputs.")

            # make sure valve's mapping is complete
            non_mapped_components = [x[0] for x in self.network if x[1] == valve and valve.mapping.get(x[0].name) is None]
            if non_mapped_components:
                raise RuntimeError(Fore.RED + f"Valve {valve} has incomplete mapping. No mapping for {non_mapped_components}")

        return True

    def describe(self):
        '''Generates a human-readable description of the apparatus.

        Returns:
            str: A description of apparatus.

        Raises:
            RuntimeError: When a component cannot be described.
        '''
        def _description(element, capitalize=False):
            '''takes a component and converts it to a string description'''
            if issubclass(element.__class__, Vessel):
                return f"{'A' if capitalize else 'a'} vessel containing {element.description}"
            elif issubclass(element.__class__, Component):
                return element.__class__.__name__ + " " + element.name
            else:
                raise RuntimeError(Fore.RED + f"{element} cannot be described. If you're seeing this message, something *very* wrong has happened.")

        result = ""

        # iterate over the network and describe the connections
        for element in self.network:
            from_component, to_component, tube = _description(element[0], capitalize=True), _description(element[1]), element[2]
            result += f"{from_component} was connected to {to_component} using {element[2].material} tubing (length {element[2].length}, ID {element[2].ID}, OD {element[2].OD}). "
        print(result)
        return result

class Protocol(object):
    '''A set of procedures for an apparatus.

    A protocol is defined as a list of procedures, atomic steps for the individual active components of an apparatus.

    Note:
        The same :class:`Apparatus` object can create multiple distinct :class:`Protocol` objects.

    Attributes:
        apparatus (Apparatus): The apparatus for which the protocol is being defined.
        duration (str, optional): The duration of the protocol.
            If None, every step will require an explicit start and stop time.
            If "auto", the duration will be inferred, if possible, during compilation as the end of last procedure in
            protocol.
            If a string, such as "3 minutes", the duration will be explicitly defined. Defaults to None.
        name (str, optional): The name of the protocol. Defaults to "Protocol_X" where *X* is protocol count.
    '''
    _id_counter = 0

    def __init__(self, apparatus, duration=None, name=None):
        assert type(apparatus) == Apparatus
        if apparatus.validate(): # ensure apparatus is valid
            self.apparatus = apparatus
        self.procedures = []
        if name is not None:
            self.name = name
        else:
            self.name = "Protocol_" + str(Protocol._id_counter)
            Protocol._id_counter += 1

        # check duration, if given
        if duration not in [None, "auto"]:
            duration = ureg.parse_expression(duration)
            if duration.dimensionality != ureg.hours.dimensionality:
                raise ValueError(Fore.RED + f"{duration.dimensionality} is an invalid unit of measurement for duration. Must be {ureg.hours.dimensionality}")
        self.duration = duration

    def _add_single(self, component, start="0 seconds", stop=None, duration=None, **kwargs):
        '''Adds a single procedure to the protocol.

        See add() for full documentation.
        '''

        # make sure that the component being added to the protocol is part of the apparatus
        if component not in self.apparatus.components:
            raise ValueError(Fore.RED + f"{component} is not a component of {self.apparatus.name}.")

        # perform the mapping for valves
        if issubclass(component.__class__, Valve) and kwargs.get("setting") is not None:
            try:
                kwargs["setting"] = component.mapping[kwargs["setting"]]
            except KeyError:
                # allow direct specification of valve settings
                if type(kwargs["setting"]) == int:
                    pass

        # don't let users give empty procedures
        if not kwargs:
            raise RuntimeError(Fore.RED + "No kwargs supplied. This will not manipulate the state of your sythesizer. Ensure your call to add() is valid.")

        # make sure the component and keywords are valid
        for kwarg, value in kwargs.items():

            if not hasattr(component, kwarg):
                raise ValueError(Fore.RED + f"Invalid attribute {kwarg} for {component}. Valid attributes are {[x for x in vars(component).keys() if x != 'name']}.")

            if type(component.__dict__[kwarg]) == ureg.Quantity and ureg.parse_expression(value).dimensionality != component.__dict__[kwarg].dimensionality:
                raise ValueError(
                    Fore.RED + f"Bad dimensionality of {kwarg} for {component}. Expected dimensionality of {component.__dict__[kwarg].dimensionality} but got {ureg.parse_expression(value).dimensionality}.")

            elif type(component.__dict__[kwarg]) != type(value) and type(component.__dict__[kwarg]) != ureg.Quantity:
                raise ValueError(Fore.RED + f"Bad type matching. Expected {kwarg} to be {type(component.__dict__[kwarg])} but got {value}, which is of type {type(value)}")

        if stop is not None and duration is not None:
            raise RuntimeError(Fore.RED + "Must provide one of stop and duration, not both.")

        # parse the start time if given
        if isinstance(start, timedelta):
            start = str(start.total_seconds()) + " seconds"
        start = ureg.parse_expression(start)

        # parse duration if given
        if duration is not None:
            if isinstance(duration, timedelta):
                duration = str(duration.total_seconds()) + " seconds"
            stop = start + ureg.parse_expression(duration)

        # determine stop time
        if stop is None and self.duration is None and duration is None:
            raise RuntimeError(Fore.RED + "Must specify protocol duration during instantiation in order to omit stop and duration. "
                               f"To automatically set duration of protocol as end of last procedure in protocol, use duration=\"auto\" when creating {self.name}.")
        elif stop is not None:
            if isinstance(stop, timedelta):
                stop = str(stop.total_seconds()) + " seconds"
            if type(stop) == str:
                stop = ureg.parse_expression(stop)

        # a little magic for temperature controllers
        if issubclass(component.__class__, TempControl):
            if kwargs.get("temp") is not None and kwargs.get("active") is None:
                kwargs["active"] = True
            elif kwargs.get("active") == False and kwargs.get("temp") is None:
                kwargs["temp"] = "0 degC"
            elif kwargs["active"] and kwargs.get("temp") is None:
                raise RuntimeError(Fore.RED + f"TempControl {component} is activated but temperature setting is not given. Specify 'temp' in your call to add().")

        # add the procedure to the procedure list
        self.procedures.append(dict(start=start, stop=stop, component=component, params=kwargs))

    def add(self, component, start="0 seconds", stop=None, duration=None, **kwargs):
        '''Adds a procedure to the protocol.

        Warning:
            If stop and duration are both None, the procedure's stop time will be inferred as the end of the protocol.

        Args:
            component_added (ActiveComponent or Iterable): The component(s) for which the procedure being added. If an
                interable, all components will have the same parameters.
            start (str, optional): The start time of the procedure relative to the start of the protocol, such as
                ``"5 seconds"``. May also be a :class:`datetime.timedelta`. Defaults to ``"0 seconds"``, *i.e.* the
                beginning of the protocol.
            stop (str, optional): The stop time of the procedure relative to the start of the protocol, such as
                ``"30 seconds"``. May also be a :class:`datetime.timedelta`. May not be given if ``duration`` is
                used. Defaults to None.
            duration (str, optional): The duration of the procedure, such as "1 hour". May also be a
                :class:`datetime.timedelta`. May not be used if ``stop`` is used. Defaults to None.
            **kwargs: The state of the component for the procedure.

        Raises:
            TypeError: A component is not of the correct type (*i.e.* a Component object)
            ValueError: An error occurred when attempting to parse the kwargs.
            RuntimeError: Stop time of procedure is unable to be determined or invalid component.
        '''

        try:
            iter(component)
        except TypeError:
            component = [component]

        for _component in component:
            self._add_single(_component, start=start, stop=stop, duration=duration, **kwargs)

    def compile(self, warnings=True, _visualization=False):
        '''Compile the protocol into a dict of devices and their procedures.

        Args:
            warnings (bool, optional): Whether to warn the user of automatic inferences and non-fatal issues.
                Default (and *highly* recommended setting) is True.

        Returns:
            dict: A dict with the names of components as the values and lists of their procedures as the value.
            The elements of the list of procedures are dicts with two keys: "time", whose value is a pint Quantity,
            and "params", whose value is a dict of parameters for the procedure.

        Raises:
            RuntimeError: When compilation fails.
        '''
        output = {}

        # infer the duration of the protocol
        if self.duration == "auto":
            self.duration = sorted([x["stop"] for x in self.procedures], key=lambda z: z.to_base_units().magnitude if type(z) == ureg.Quantity else 0)
            if all([x == None for x in self.duration]):
                raise RuntimeError(Fore.RED + "Unable to automatically infer duration of protocol. Must define stop for at least one procedure to use duration=\"auto\".")
            self.duration = self.duration[-1]

        # deal only with compiling active components
        for component in [x for x in self.apparatus.components if issubclass(x.__class__, ActiveComponent)]:
            # make sure all active components are activated, raising warning if not
            if component not in [x["component"] for x in self.procedures]:
                if warnings:
                    warn(Fore.YELLOW + f"{component} is an active component but was not used in this procedure. If this is intentional, ignore this warning. To suppress this warning, use warnings=False.")

            # determine the procedures for each component
            component_procedures = sorted([x for x in self.procedures if x["component"] == component], key=lambda x: x["start"])

            # skip compilation of components with no procedures added
            if not len(component_procedures):
                continue

            # check for conflicting continuous procedures
            if len([x for x in component_procedures if x["start"] is None and x["stop"] is None]) > 1:
                raise RuntimeError(Fore.RED + (f"{component} cannot have two procedures for the entire duration of the protocol. "
                                               "If each procedure defines a different attribute to be set for the entire duration, combine them into one call to add(). "
                                               "Otherwise, reduce ambiguity by defining start and stop times for each procedure."))

            for i, procedure in enumerate(component_procedures):
                # ensure that the start time is before the stop time if given
                if procedure["stop"] is not None and procedure["start"] > procedure["stop"]:
                    raise RuntimeError(Fore.RED + "Start time must be less than or equal to stop time.")

                # make sure that the start time isn't outside the duration
                if self.duration is not None and procedure["start"] is not None and procedure["start"] > self.duration:
                    raise ValueError(Fore.RED + f"Procedure cannot start at {procedure['start']}, which is outside the duration of the experiment ({self.duration}).")

                # make sure that the end time isn't outside the duration
                if self.duration is not None and procedure["stop"] is not None and procedure["stop"] > self.duration:
                    raise ValueError(Fore.RED + f"Procedure cannot end at {procedure['stop']}, which is outside the duration of the experiment ({self.duration}).")

                # automatically infer start and stop times
                try:
                    if component_procedures[i + 1]["start"] == ureg.parse_expression("0 seconds"):
                        raise RuntimeError(Fore.RED + f"Ambiguous start time for {procedure['component']}.")
                    elif component_procedures[i + 1]["start"] is not None and procedure["stop"] is None:
                        if warnings:
                            warn(
                                Fore.YELLOW + f"Automatically inferring stop time for {procedure['component']} as beginning of {procedure['component']}'s next procedure. To suppress this warning, use warnings=False.")
                        procedure["stop"] = component_procedures[i + 1]["start"]
                except IndexError:
                    if procedure["stop"] is None:
                        if warnings:
                            warn(
                                Fore.YELLOW + f"Automatically inferring stop for {procedure['component']} as the end of the protocol. To override, provide stop in your call to add(). To suppress this warning, use warnings=False.")
                        procedure["stop"] = self.duration

            # give the component instructions at all times
            compiled = []
            for i, procedure in enumerate(component_procedures):
                if _visualization:
                    compiled.append(dict(start=procedure["start"], stop=procedure["stop"], params=procedure["params"]))
                else:
                    compiled.append(dict(time=procedure["start"], params=procedure["params"]))

                    # if the procedure is over at the same time as the next procedure begins, don't go back to the base state
                    try:
                        if component_procedures[i + 1]["start"] == procedure["stop"]:
                            continue
                    except IndexError:
                        pass

                    # otherwise, go back to base state
                    compiled.append(dict(time=procedure["stop"], params=component.base_state()))

            output[component] = compiled

            # raise warning if duration is explicitly given but not used?
        return output

    def json(self, warnings=True):
        '''Compiles protocol and outputs to JSON.

        Args:
            warnings (bool, optional): See :meth:`Protocol.compile` for full explanation of this argument.

        Returns:
            str: JSON of the compiled protocol.

        Raises:
            Same as :meth:`Protocol.compile`.
        '''
        compiled = deepcopy(self.compile(warnings=warnings))
        for item in compiled.items():
            for procedure in item[1]:
                procedure["time"] = procedure["time"].to_timedelta().total_seconds()
        compiled = {k.name: v for (k, v) in compiled.items()}
        return json.dumps(compiled, indent=4, sort_keys=True)

    def yaml(self, warnings=True):
        '''Compiles protocol and outputs to YAML.

        Internally, this is a conversion of the output of :meth:`Protocol.json`
        for the purpose of enhanced human readability.

        Args:
            warnings (bool, optional): See :meth:`Protocol.compile` for full explanation of this argument.

        Returns:
            str: YAML of the compiled protocol.

        Raises:
            Same as :meth:`Protocol.compile`.
        '''
        return yaml.safe_dump(json.loads(self.json(warnings=warnings)))

    def visualize(self, browser=True):
        '''Generates a Gantt plot visualization of the protocol.

        Note:
            Each value of a parameter will have a consistent color, but some colors may be reused.

        Args:
            browser (bool, optional): Whether to open in the browser. Defaults to true.

        Returns:
            str: The html of the visualization.

        Raises:
            ImportError: When the visualization package is not installed.
        '''

        # set up the temporary file
        tmp = tempfile.NamedTemporaryFile(delete=False)
        path = tmp.name + '.html'
        f = open(path, 'w')

        # render the html
        env = Environment(autoescape=select_autoescape(['html', 'xml']),
                          loader=PackageLoader("mechwolf", "templates"))
        template = env.get_template('visualizer.html')
        visualization = template.render(title=self.name, procedures=self.procedures)

        # write to the temp file
        f.write(visualization)
        f.close()

        # open it up in the default webbrowser
        if browser:
            webbrowser.open("file://" + f.name)

        return visualization

    def execute(self, address=None, hub_id=None, security_key=None, confirmation=True):
        '''Executes the procedure.

        When a ``hub_id`` and ``security_key`` are not provided, there will be a
        command line prompt with the  option to save them to the keychain.
        Subsequent invocations of this function will not prompt the user  for
        the ``hub_id`` and ``security_key``.

        To change the stored values of ``hub_id`` and ``security_key``, run this command::

            $ mechwolf update

        For more information, run::

            $ mechwolf update --help

        Providing ``hub_id`` and ``security_key`` as keyword arguments will
        override stored values and will not save the new values to the keychain.

        Warning:
            If providing ``security_key`` as a keyword argument, do not share your source code.

        Args:
            address (str, optional): The address of the hub to connect to. If None, the MechWolf resolver is used.
            hub_id (str, optional): The hub id to which the protocol should be sent. If None, it is requested via command line.
            security_key (str, optional): The security key of the hub to which the protocol is being sent. If None, it is requested via command line.
            confirmation (bool, optional): Whether to ask for confirmation. Defaults to True.

        Note:
            Must only contain :class:`~mechwolf.components.component.ActiveComponent` s that have an
            update method, i.e. real components.

        Raises:
            RuntimeError: When attempting to execute a protocol on invalid components.
        '''

        # Ensure that execution isn't happening on invalid components
        if not all([validate_component(x["component"]) for x in self.procedures]):
            raise RuntimeError(Fore.RED + f"Attempting to execute protocol on invalid component {component}. Aborted.")

        # get hub_id
        if hub_id is None:
            if keyring.get_password("mechwolf", "hub_id") is None:
                hub_id = prompt("Please enter your hub_id", type=str)
                if confirm("Save hub_id?", default=True):
                    keyring.set_password("mechwolf", "hub_id", hub_id)
                    print("Storing hub_id! To change, run the command: $ mechwolf update")
            else:
                hub_id = keyring.get_password("mechwolf", "hub_id")

        # get security_key
        if security_key is None:
            if keyring.get_password("mechwolf", "security_key") is None:
                security_key = prompt("Please enter your security_key", type=str)
                if confirm("Save security_key?", default=True):
                    keyring.set_password("mechwolf", "security_key", security_key)
                    print("Storing security_key! To change, run the command: $ mechwolf update")
            else:
                security_key = keyring.get_password("mechwolf", "security_key")
        else:
            print(Fore.YELLOW + "Remember never to share source code containing your security key!")

        signer = itsdangerous.Signer(security_key)
        serializer = itsdangerous.URLSafeTimedSerializer(security_key)
        timestamp_signer = itsdangerous.TimestampSigner(security_key)

        if confirmation:
            confirm("Are you sure you want to execute this procedure?", abort=True, default=True)

        # get the address
        if address is None:
            response = requests.request("GET", RESOLVER_URL + "get_hub", params={"hub_id": hub_id})
            try:
                address = signer.unsign(response.json()["hub_address"]).decode()
            except json.decoder.JSONDecodeError:
                raise RuntimeError(Fore.RED + "Invalid hub_id. Ensure that you have the correct hub_id. "
                                              "To update the hub_id stored on this device, run 'mechwolf update'. "
                                              "To update your client or hub, update their config file.")

        # subit the protocol to the hub
        try:
            response = requests.post(f"https://{address}/submit_protocol", data=dict(protocol=serializer.dumps(self.json())), verify=False).text
            response = timestamp_signer.unsign(response).decode()
            if response == "protocol rejected: different protocol being executed":
                raise RuntimeError(Fore.RED + "Protocol rejected because hub is currently executing a different protocol.")
            elif response != "protocol rejected: invalid signature":
                print(f"Protocol id: {response}")
                return
        except itsdangerous.BadSignature:
            pass
        raise RuntimeError(Fore.RED + "Bad signature! Make sure that your security key is correct in both places.")
