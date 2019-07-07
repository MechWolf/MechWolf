import asyncio
import json
import tempfile
import webbrowser
from collections import defaultdict
from copy import deepcopy
from datetime import timedelta
from typing import NamedTuple, Union
from warnings import warn

import yaml
from IPython.display import HTML, Code, display
from jinja2 import Environment, PackageLoader, select_autoescape
from loguru import logger

from . import ureg
from .apparatus import Apparatus
from .components import TempControl, Valve
from .execute import main
from .experiment import Experiment


class Procedure(NamedTuple):
    duration: Union[float, None]
    params: dict


class CompiledProcedure(NamedTuple):
    start: float
    params: dict


class Protocol(object):
    """A set of procedures for an apparatus.

    A protocol is defined as a list of procedures, atomic steps for the individual active components of an apparatus.

    Note:
        The same :class:`Apparatus` object can create multiple distinct :class:`Protocol` objects.

    Attributes:
        apparatus (Apparatus): The apparatus for which the protocol is being defined.
        name (str, optional): The name of the protocol. Defaults to "Protocol_X" where *X* is protocol count.
    """

    _id_counter = 0

    def __init__(self, apparatus, name=None):
        if not isinstance(apparatus, Apparatus):
            raise TypeError(
                f"Must pass an Apparatus object. Got {type(apparatus)}, "
                "which is not an instance of mechwolf.Apparatus."
            )

        # ensure apparatus is valid
        if not apparatus.validate():
            raise ValueError("Apparaus is not valid.")

        self.apparatus = apparatus
        self.procedures = defaultdict(list)
        if name is not None:
            self.name = name
        else:
            self.name = "Protocol_" + str(Protocol._id_counter)
            Protocol._id_counter += 1

        self.is_executing = False
        self.was_executed = False

    def __repr__(self):
        return f"MechWolf protocol for Apparatus {self.apparatus}"

    @staticmethod
    def _user_provided_time_to_float(user_provided_time):
        if isinstance(user_provided_time, (int, float)):
            warn(
                f"Given time as {type(user_provided_time)} without unit. Assuming seconds."
            )
            return float(user_provided_time)
        if isinstance(user_provided_time, timedelta):
            user_provided_time = str(user_provided_time.total_seconds()) + " seconds"
        if isinstance(user_provided_time, str):
            return ureg.parse_expression(user_provided_time).to_base_units().magnitude
        raise ValueError("Unable to parse time")

    def _add_single(self, component, duration=None, **kwargs):
        """Adds a single procedure to the protocol.

        See add() for full documentation.
        """

        # make sure that the component being added to the protocol is part of the apparatus
        if component not in self.apparatus._active_components:
            raise ValueError(
                f"{component} is not a component of {self.apparatus.name}."
            )

        # perform the mapping for valves
        if issubclass(component.__class__, Valve) and kwargs.get("setting") is not None:
            try:
                kwargs["setting"] = component.mapping[kwargs["setting"]]
            except KeyError:
                # allow direct specification of valve settings
                if isinstance(kwargs["setting"], int):
                    pass

        if not kwargs:
            warn(
                "No kwargs supplied. "
                f"Assuming {component.base_state()}, which is {component}'s base state."
            )
            kwargs = component.base_state()

        # make sure the component and keywords are valid
        for kwarg, value in kwargs.items():

            if not hasattr(component, kwarg):
                raise ValueError(
                    f"Invalid attribute {kwarg} for {component}."
                    f" Valid attributes are {[x for x in vars(component).keys() if x != 'name' and not x.startswith('_')]}."
                )

            if (
                isinstance(component.__dict__[kwarg], ureg.Quantity)
                and ureg.parse_expression(value).dimensionality
                != component.__dict__[kwarg].dimensionality
            ):
                raise ValueError(
                    f"Bad dimensionality of {kwarg} for {component}. "
                    f"Expected dimensionality of {component.__dict__[kwarg].dimensionality} "
                    f"but got {ureg.parse_expression(value).dimensionality}."
                )

            elif not isinstance(
                component.__dict__[kwarg], type(value)
            ) and not isinstance(component.__dict__[kwarg], ureg.Quantity):
                raise ValueError(
                    f"Bad type matching. Expected {kwarg} to be {type(component.__dict__[kwarg])} "
                    f"but got {value}, which is of type {type(value)}"
                )

        # parse the time, if given
        if duration is not None:
            duration = self._user_provided_time_to_float(duration)

        # a little magic for temperature controllers
        if issubclass(component.__class__, TempControl):
            if kwargs.get("temp") is not None and kwargs.get("active") is None:
                kwargs["active"] = True
            elif not kwargs.get("active") and kwargs.get("temp") is None:
                kwargs["temp"] = "0 degC"
            elif kwargs["active"] and kwargs.get("temp") is None:
                raise RuntimeError(
                    f"TempControl {component} is activated but temperature "
                    "setting is not given. Specify 'temp' in your call to add()."
                )

        # quick check to prevent ambiguity
        if self.procedures[component]:
            if self.procedures[component][-1].duration is None:
                raise ValueError(
                    f"Only the last procedure for {component} may have no provided duration."
                )

        self.procedures[component].append(Procedure(duration=duration, params=kwargs))

    def add(self, component, duration=None, **kwargs):
        """Adds a procedure to the protocol.

        Note:
            You may only call this function once per component with ``duration=None``.

        Args:
            component (ActiveComponent or Iterable): The component(s) for which the procedure being added. If an
                interable, all components will have the same parameters.
            duration (str, optional): The duration of the procedure, such as "1 hour". May also be a
                :class:`datetime.timedelta`. May not be used if ``stop`` is used. Defaults to None.
            **kwargs: The state of the component for the procedure.

        Raises:
            TypeError: A component is not of the correct type (*i.e.* a Component object)
            ValueError: An error occurred when attempting to parse the kwargs.
            RuntimeError: Stop time of procedure is unable to be determined or invalid component.
        """

        try:
            iter(component)
        except TypeError:
            component = [component]

        for _component in component:
            self._add_single(_component, duration=duration, **kwargs)

    def compile(self, dry_run=True, _visualization=False):
        """Compile the protocol into a dict of devices and their procedures.

        Returns:
            dict: A dict with the names of components as the values and lists of their procedures as the value.
            The elements of the list of procedures are dicts with two keys: "time", whose value is a pint Quantity,
            and "params", whose value is a dict of parameters for the procedure.

        Raises:
            RuntimeError: When compilation fails.
        """
        # perform check that all ActiveComponents are used
        logger.trace("Performing check that all given ActiveComponents are used...")
        unused_active_components = self.apparatus._active_components - set(
            self.procedures.keys()
        )
        if unused_active_components:
            if len(unused_active_components) == 1:
                warn(
                    f"{list(unused_active_components)[0]} is an ActiveComponent "
                    "but was not used in this procedure. If this is intentional, "
                    "ignore this warning."
                )
            else:
                warn(
                    f"{list(unused_active_components)} are ActiveComponents but "
                    "were not used in this procedure. If this is intentional, "
                    "ignore this warning."
                )

        # infer the overall duration of the protocol
        duration = 0
        for k, v in self.procedures.items():
            if v[-1].duration is not None:
                c_duration = sum(procedure.duration for procedure in v)
                if c_duration > duration:
                    duration = c_duration
            else:
                c_duration = sum(procedure.duration for procedure in v[:-1])
                if c_duration > duration:
                    duration = c_duration

        if duration == 0:
            raise RuntimeError(
                "Unable to automatically infer duration of protocol "
                "or the duration of the protocol would be 0."
            )

        # this will be the final result
        compiled = {}

        for component, procedures in self.procedures.items():

            # make sure all active components are activated, raising warning if not
            if not component.validate(dry_run=dry_run):
                raise RuntimeError("Component is not valid.")

            # now to convert durations to start times
            start_time = 0
            compiled_procedures = []
            for procedure in procedures:
                # we start off at t=0
                compiled_procedures.append(
                    CompiledProcedure(start=start_time, params=procedure.params)
                )
                # and then add the duration (in seconds)
                try:
                    start_time += procedure.duration
                # in case of a failure, we'll handle it right away
                except TypeError:
                    break

            # be sure to execute the final procedure for the right duration
            if procedures[-1].duration is not None:
                compiled_procedures.append(
                    CompiledProcedure(start=start_time, params=component.base_state())
                )

            # finally, turn off the component
            compiled_procedures.append(
                CompiledProcedure(start=duration, params=component.base_state())
            )

            # now we have the fully compiled procedures
            compiled[component] = compiled_procedures

        return compiled

    def to_dict(self):
        compiled = deepcopy(self.compile(dry_run=True))
        for item in compiled.items():
            for procedure in item[1]:
                procedure["time"] = procedure["time"].to_timedelta().total_seconds()
        compiled = {k.name: v for (k, v) in compiled.items()}
        return compiled

    def to_list(self):
        output = []
        for procedure in deepcopy(self.procedures):
            procedure["start"] = procedure["start"].to_timedelta().total_seconds()
            procedure["stop"] = procedure["stop"].to_timedelta().total_seconds()
            procedure["component"] = procedure["component"].name
            output.append(procedure)
        return output

    def yaml(self):
        """Outputs

         procedures to YAML.

        Internally, this is a conversion of the output of :meth:`Protocol.json`
        for the purpose of enhanced human readability.

        Returns:
            str: YAML of the procedure list. When in Jupyter, this string is wrapped in a :class:`IPython.display.Code` object for nice syntax highlighting.

        """
        compiled_yaml = yaml.safe_dump(self.to_list(), default_flow_style=False)

        try:
            get_ipython
            return Code(compiled_yaml, language="yaml")
        except NameError:
            pass
        return compiled_yaml

    def json(self):
        """Outputs procedures to JSON.

        Returns:
            str: JSON of the protocol. When in Jupyter, this string is wrapped in a :class:`IPython.display.Code` object for nice syntax highlighting.
        """
        compiled_json = json.dumps(self.to_list(), sort_keys=True, indent=4)

        try:
            get_ipython
            return Code(compiled_json, language="json")
        except NameError:
            pass
        return compiled_json

    def visualize(self, browser=True):
        """Generates a Gantt plot visualization of the protocol.

        Args:
            browser (bool, optional): Whether to open in the browser. Defaults to true.

        Returns:
            str: The html of the visualization. When in Jupyter, this string is wrapped in a :class:`IPython.display.HTML` object for interactive display.

        Raises:
            ImportError: When the visualization package is not installed.
        """

        # render the html
        env = Environment(
            autoescape=select_autoescape(["html", "xml"]),
            loader=PackageLoader("mechwolf", "templates"),
        )
        visualization = env.get_template("viz_div.html").render(
            compiled=self.compile(dry_run=True)
        )

        # show it in Jupyter, if possible
        try:
            get_ipython()
            return HTML(visualization)
        except NameError:
            pass

        template = env.get_template("visualizer.html")
        visualization = template.render(title=self.name, visualization=visualization)

        if browser:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                tmp.write(visualization.encode("utf-8"))
                webbrowser.open("file://" + tmp.name)

        return visualization

    def execute(self, dry_run=False, verbosity="info"):
        """Executes the procedure.

        Args:
            dry_run (bool, optional): Whether to simulate the experiment or
                actually perform it. Defaults to False, which means executing the
                protocol on real hardware.

            verbosity (str, optional): The level of logging verbosity. One of
                ``"critical"``, ``"error"``, ``"warning"``, ``"success"``,
                ``"info"``, ``"debug"``, or ``"trace"`` in descending order of
                severity. ``"debug"`` and (especially) ``"trace"`` are not meant to
                be used regularly, as they generate significant amounts of usually
                useless information. However, these verbosity levels are useful for
                tracing where exactly a bug was generated, especially if no error
                message was thrown. Defaults to ``"info"``.

        Note:
            Must only contain :class:`~mechwolf.components.component.ActiveComponent` s that have an
            update method, i.e. real components.

        Raises:
            RuntimeError: When attempting to execute a protocol on invalid components.
        """

        # If protocol is executing, return an error
        if self.is_executing:
            logger.error("Protocol is currently running.")
            return

        logger.info(f"Compiling protocol with dry_run = {dry_run}")
        compiled_protocol = self.compile(dry_run=dry_run)

        # the Experiment object is going to hold all the info
        E = Experiment(
            self, compiled_protocol=compiled_protocol, verbosity=verbosity.upper()
        )
        display(E._output_widget)

        self.is_executing = True

        try:
            get_ipython()
            asyncio.ensure_future(main(experiment=E, dry_run=dry_run))
        except NameError:
            asyncio.run(main(experiment=E, dry_run=dry_run))

        return E
