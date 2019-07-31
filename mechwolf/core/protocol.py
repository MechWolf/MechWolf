import asyncio
import json
import os
from copy import deepcopy
from datetime import timedelta
from math import isclose
from pathlib import Path
from typing import (
    IO,
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Union,
)
from warnings import warn

import altair as alt
import pandas as pd
import yaml
from IPython import get_ipython
from IPython.display import Code, display
from loguru import logger

from .. import _ureg
from ..components import ActiveComponent, TempControl, Valve
from .apparatus import Apparatus
from .execute import main
from .experiment import Experiment


class Protocol(object):
    """
    A set of procedures for an apparatus.

    A protocol is defined as a list of procedures, atomic steps for the individual active components of an apparatus.

    ::: tip
    The same `Apparatus` object can create multiple distinct `Protocol` objects.
    :::

    Arguments:
    - `apparatus`: The apparatus for which the protocol is being defined.
    - `name`: The name of the protocol. Defaults to "Protocol_X" where *X* is protocol count.
    - `description`: A longer description of the protocol.

    Attributes:
    - `apparatus`: The apparatus for which the protocol is being defined.
    - `description`: A longer description of the protocol.
    - `is_executing`: Whether the protocol is executing.
    - `name`: The name of the protocol. Defaults to "Protocol_X" where *X* is protocol count.
    - `procedures`: A list of the procedures for the protocol in which each procedure is a dict.
    - `was_executed`: Whether the protocol was executed.
    """

    _id_counter = 0

    def __init__(
        self,
        apparatus: Apparatus,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """See main docstring."""
        # type checking
        if not isinstance(apparatus, Apparatus):
            raise TypeError(
                f"Must pass an Apparatus object. Got {type(apparatus)}, "
                "which is not an instance of mechwolf.Apparatus."
            )

        # ensure apparatus is valid
        if not apparatus._validate():
            raise ValueError("Apparaus is not valid.")

        # store the passed args
        self.apparatus = apparatus
        self.description = description

        # generate the name
        if name is not None:
            self.name = name
        else:
            self.name = "Protocol_" + str(Protocol._id_counter)
            Protocol._id_counter += 1

        # default values
        self.procedures: List[
            Dict[str, Union[float, None, ActiveComponent, Dict[str, Any]]]
        ] = []
        self.was_executed = False

        # internal values
        self._file_logger_id: Optional[int] = None
        self._is_executing = False
        self._log_file: Union[IO, str, None, os.PathLike] = None
        self._data_file: Optional[os.PathLike] = None

    def __repr__(self):
        return f"<{self.__str__()}>"

    def __str__(self):
        return f"Protocol {self.name} defined over {repr(self.apparatus)}"

    def _add_single(
        self,
        component: ActiveComponent,
        start="0 seconds",
        stop=None,
        duration=None,
        **kwargs,
    ) -> None:
        """Adds a single procedure to the protocol.

        See add() for full documentation.
        """

        # make sure that the component being added to the protocol is part of the apparatus
        if component not in self.apparatus.components:
            raise ValueError(
                f"{component} is not a component of {self.apparatus.name}."
            )

        # perform the mapping for valves
        if isinstance(component, Valve) and isinstance(component.mapping, Mapping):
            setting = kwargs["setting"]

            # the component itself was given
            if setting in component.mapping:
                logger.trace(f"{setting} in {repr(component)}'s mapping.")
                kwargs["setting"] = component.mapping[setting]

            # the component's name was given
            # in this case, we get the mapped component with that name
            # we don't have to worry about duplicate names since that's checked later
            elif setting in [c.name for c in component.mapping]:
                logger.trace(f"{setting} in {repr(component)}'s mapping.")
                mapped_component = [c for c in component.mapping if c.name == setting]
                kwargs["setting"] = component.mapping[mapped_component[0]]

            # the user gave the actual port mapping number
            elif setting in component.mapping.values() and isinstance(setting, int):
                logger.trace(f"User supplied manual setting for {component}")
            else:
                raise ValueError(f"Invalid setting {setting} for {repr(component)}.")

        # don't let users give empty procedures
        if not kwargs:
            raise RuntimeError(
                "No kwargs supplied. "
                "This will not manipulate the state of your sythesizer. "
                "Ensure your call to add() is valid."
            )

        # make sure the component and keywords are valid
        for kwarg, value in kwargs.items():

            if not hasattr(component, kwarg):
                raise ValueError(
                    f"Invalid attribute {kwarg} for {component}."
                    f" Valid attributes are {[x for x in vars(component).keys() if x != 'name' and not x.startswith('_')]}."
                )

            if (
                isinstance(component.__dict__[kwarg], _ureg.Quantity)
                and _ureg.parse_expression(value).dimensionality
                != component.__dict__[kwarg].dimensionality
            ):
                raise ValueError(
                    f"Bad dimensionality of {kwarg} for {component}. "
                    f"Expected dimensionality of {component.__dict__[kwarg].dimensionality} "
                    f"but got {_ureg.parse_expression(value).dimensionality}."
                )

            elif not isinstance(
                component.__dict__[kwarg], type(value)
            ) and not isinstance(component.__dict__[kwarg], _ureg.Quantity):
                raise ValueError(
                    f"Bad type matching. Expected '{kwarg}' to be {type(component.__dict__[kwarg])} "
                    f"but got {repr(value)}, which is of type {type(value)}"
                )

        if stop is not None and duration is not None:
            raise RuntimeError("Must provide one of stop and duration, not both.")

        # parse the start time if given
        if isinstance(start, timedelta):
            start = str(start.total_seconds()) + " seconds"
        start = _ureg.parse_expression(start)

        # parse duration if given
        if duration is not None:
            if isinstance(duration, timedelta):
                duration = str(duration.total_seconds()) + " seconds"
            stop = start + _ureg.parse_expression(duration)
        elif stop is not None:
            if isinstance(stop, timedelta):
                stop = str(stop.total_seconds()) + " seconds"
            if isinstance(stop, str):
                stop = _ureg.parse_expression(stop)

        if start is not None and stop is not None and start > stop:
            raise ValueError("Procedure beginning is after procedure end.")

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

        # add the procedure to the procedure list
        self.procedures.append(
            dict(
                start=float(start.to_base_units().magnitude)
                if start is not None
                else start,
                stop=float(stop.to_base_units().magnitude)
                if stop is not None
                else stop,
                component=component,
                params=kwargs,
            )
        )

    def add(
        self,
        component: Union[ActiveComponent, Iterable[ActiveComponent]],
        start="0 seconds",
        stop=None,
        duration=None,
        **kwargs,
    ):
        """
        Adds a procedure to the protocol.

        ::: warning
        If stop and duration are both `None`, the procedure's stop time will be inferred as the end of the protocol.
        :::

        Arguments:
        - `component_added`: The component(s) for which the procedure being added. If an interable, all components will have the same parameters.
        - `start`: The start time of the procedure relative to the start of the protocol, such as `"5 seconds"`. May also be a `datetime.timedelta`. Defaults to `"0 seconds"`, *i.e.* the beginning of the protocol.
        - `stop`: The stop time of the procedure relative to the start of the protocol, such as `"30 seconds"`. May also be a `datetime.timedelta`. May not be given if `duration` is used.
        duration: The duration of the procedure, such as "1 hour". May not be used if `stop` is used.
        - `**kwargs`: The state of the component for the procedure.

        Raises:
        - `TypeError`: A component is not of the correct type (*i.e.* a Component object)
        - `ValueError`: An error occurred when attempting to parse the kwargs.
        - `RuntimeError`: Stop time of procedure is unable to be determined or invalid component.
        """

        if isinstance(component, Iterable):
            for _component in component:
                self._add_single(
                    _component, start=start, stop=stop, duration=duration, **kwargs
                )
        else:
            self._add_single(
                component, start=start, stop=stop, duration=duration, **kwargs
            )

    @property
    def _inferred_duration(self):
        # infer the duration of the protocol
        computed_durations = sorted(
            [x["stop"] for x in self.procedures],
            key=lambda z: z if z is not None else 0,
        )
        if all([x is None for x in computed_durations]):
            raise RuntimeError(
                "Unable to automatically infer duration of protocol. "
                'Must define stop or duration for at least one procedure to use duration="auto".'
            )
        return computed_durations[-1]

    @property
    def is_executing(self):
        return self._is_executing

    @is_executing.setter
    def is_executing(self, is_executing):
        if not is_executing and self._file_logger_id is not None:
            logger.info("Wrote logs to " + str(self._log_file.absolute()))
            logger.trace(f"Removing generated file logger {self._file_logger_id}")
            logger.remove(self._file_logger_id)
            logger.trace("File logger removed")
            # ensure that an execution without logging after one with it doesn't break
            self._log_file = None
            self._file_logger_id = None
        if not is_executing and self._data_file:
            logger.info("Wrote data to " + str(self._data_file.absolute()))
            logger._data_file = None
        logger.debug(f"{repr(self)}.is_executing is now {is_executing}")
        self._is_executing = is_executing

    def _compile(
        self, dry_run: bool = True, _visualization: bool = False
    ) -> Dict[ActiveComponent, List[Dict[str, Union[float, str, Dict[str, Any]]]]]:
        """
        Compile the protocol into a dict of devices and their procedures.

        Returns:
        - A dict with components as the values and lists of their procedures as the value.
        The elements of the list of procedures are dicts with two keys: "time" in seconds, and "params", whose value is a dict of parameters for the procedure.

        Raises:
        - `RuntimeError`: When compilation fails.
        """
        output = {}

        # deal only with compiling active components
        for component in self.apparatus[ActiveComponent]:
            # determine the procedures for each component
            component_procedures: List[MutableMapping] = sorted(
                [x for x in self.procedures if x["component"] == component],
                key=lambda x: x["start"],
            )

            # skip compiling components without procedures
            if not len(component_procedures):
                warn(
                    f"{component} is an active component but was not used in this procedure."
                    " If this is intentional, ignore this warning."
                )
                continue

            # validate each component
            try:
                component._validate(dry_run=dry_run)
            except Exception as e:
                raise RuntimeError(f"{component} isn't valid. Got error: '{str(e)}'.")

            # check for conflicting continuous procedures
            if (
                len(
                    [
                        x
                        for x in component_procedures
                        if x["start"] is None and x["stop"] is None
                    ]
                )
                > 1
            ):
                raise RuntimeError(
                    f"{component} cannot have two procedures for the entire duration of the protocol. "
                    "If each procedure defines a different attribute to be set for the entire duration, "
                    "combine them into one call to add(). Otherwise, reduce ambiguity by defining start "
                    "and stop times for each procedure. "
                    ""
                )

            for i, procedure in enumerate(component_procedures):

                # automatically infer start and stop times
                try:
                    if component_procedures[i + 1]["start"] == 0:
                        raise RuntimeError(
                            f"Ambiguous start time for {procedure['component']}. " ""
                        )
                    elif (
                        component_procedures[i + 1]["start"] is not None
                        and procedure["stop"] is None
                    ):
                        warn(
                            f"Automatically inferring stop time for {procedure['component']} "
                            f"as beginning of {procedure['component']}'s next procedure."
                        )
                        procedure["stop"] = component_procedures[i + 1]["start"]
                except IndexError:
                    if procedure["stop"] is None:
                        warn(
                            f"Automatically inferring stop for {procedure['component']} as "
                            f"the end of the protocol. To override, provide stop in your call to add()."
                        )
                        procedure["stop"] = self._inferred_duration

            # give the component instructions at all times
            compiled = []
            for i, procedure in enumerate(component_procedures):
                if _visualization:
                    compiled.append(
                        dict(
                            start=procedure["start"],
                            stop=procedure["stop"],
                            params=procedure["params"],
                        )
                    )
                else:
                    compiled.append(
                        dict(time=procedure["start"], params=procedure["params"])
                    )

                    # if the procedure is over at the same time as the next
                    # procedure begins, don't go back to the base state
                    try:
                        if isclose(
                            component_procedures[i + 1]["start"], procedure["stop"]
                        ):
                            continue
                    except IndexError:
                        pass

                    # otherwise, go back to base state
                    compiled.append(
                        dict(time=procedure["stop"], params=component._base_state())
                    )

            output[component] = compiled

            # raise warning if duration is explicitly given but not used?
        return output

    def to_dict(self):
        compiled = deepcopy(self._compile(dry_run=True))
        compiled = {k.name: v for (k, v) in compiled.items()}
        return compiled

    def to_list(self):
        output = []
        for procedure in deepcopy(self.procedures):
            procedure["component"] = procedure["component"].name
            output.append(procedure)
        return output

    def yaml(self) -> Union[str, Code]:
        """
        Outputs the uncompiled procedures to YAML.

        Internally, this is a conversion of the output of `Protocol.json` for the purpose of enhanced human readability.

        Returns:
        - YAML of the procedure list.
        When in Jupyter, this string is wrapped in an `IPython.display.Code` object for nice syntax highlighting.

        """
        compiled_yaml = yaml.safe_dump(self.to_list(), default_flow_style=False)

        if get_ipython():
            return Code(compiled_yaml, language="yaml")
        return compiled_yaml

    def json(self) -> Union[str, Code]:
        """
        Outputs the uncompiled procedures to JSON.

        Returns:
        - JSON of the protocol.
          When in Jupyter, this string is wrapped in a `IPython.display.Code` object for nice syntax highlighting.
        """
        compiled_json = json.dumps(self.to_list(), sort_keys=True, indent=4)

        if get_ipython():
            return Code(compiled_json, language="json")
        return compiled_json

    def visualize(self, legend: bool = False, width=500, renderer: str = "notebook"):
        """
        Generates a Gantt plot visualization of the protocol.

        Arguments:
        - `legend`: Whether to show a legend.
        - `renderer`: Which renderer to use. Defaults to "notebook" but can also be "jupyterlab", or "nteract", depending on the development environment. If not in a Jupyter Notebook, this argument is ignored.
        - `width`: The width of the Gantt chart.

        Returns:
        - An interactive visualization of the protocol.
        """

        # don't try to render a visualization to the notebook if we're not in one
        if get_ipython():
            alt.renderers.enable(renderer)

        for component, procedures in self._compile(_visualization=True).items():
            # generate a dict that will be a row in the dataframe
            for procedure in procedures:
                procedure["component"] = str(component)
                procedure["start"] = pd.Timestamp(procedure["start"], unit="s")
                procedure["stop"] = pd.Timestamp(procedure["stop"], unit="s")

                # hoist the params to the main dict
                assert isinstance(procedure["params"], dict)  # needed for typing
                for k, v in procedure["params"].items():
                    procedure[k] = v

                # TODO: make this deterministic for color coordination
                procedure["params"] = json.dumps(procedure["params"])

            # prettyify the tooltips
            tooltips = [
                alt.Tooltip("utchoursminutesseconds(start):T", title="Start (h:m:s)"),
                alt.Tooltip("utchoursminutesseconds(stop):T", title="Stop (h:m:s)"),
                "component",
            ]

            # just add the params to the tooltip
            tooltips.extend(
                [
                    x
                    for x in procedures[0].keys()
                    if x not in ["component", "start", "stop", "params"]
                ]
            )

            # generate the component's graph
            source = pd.DataFrame(procedures)
            component_chart = (
                alt.Chart(source, width=width)
                .mark_bar()
                .encode(
                    x="utchoursminutesseconds(start):T",
                    x2="utchoursminutesseconds(stop):T",
                    y="component",
                    color=alt.Color("params:N", legend=None)
                    if not legend
                    else "params",
                    tooltip=tooltips,
                )
            )

            # label the axes
            component_chart.encoding.x.title = "Experiment Elapsed Time (h:m:s)"
            component_chart.encoding.y.title = "Component"

            # combine with the other charts
            try:
                chart += component_chart  # type: ignore
            except NameError:
                chart = component_chart

        return chart.interactive()

    def execute(
        self,
        dry_run: Union[bool, int] = False,
        verbosity: str = "info",
        confirm: bool = False,
        strict: bool = True,
        log_file: Union[str, bool, os.PathLike] = True,
        log_file_verbosity: Optional[str] = None,
        log_file_compression: Optional[str] = None,
        data_file: Union[str, bool, os.PathLike] = True,
    ) -> Experiment:
        """
        Executes the procedure.

        Arguments:
        - `confirm`: Whether to bypass the manual confirmation message before execution.
        - `dry_run`: Whether to simulate the experiment or actually perform it. Defaults to `False`, which means executing the protocol on real hardware. If an integer greater than zero, the dry run will execute at that many times speed.
        - `strict`: Whether to stop execution upon encountering any errors. If False, errors will be noted but ignored.
        - `verbosity`: The level of logging verbosity. One of "critical", "error", "warning", "success", "info", "debug", or "trace" in descending order of severity. "debug" and (especially) "trace" are not meant to be used regularly, as they generate significant amounts of usually useless information. However, these verbosity levels are useful for tracing where exactly a bug was generated, especially if no error message was thrown.
        - `log_file`: The file to write the logs to during execution. If `True`, the data will be written to a file in `~/.mechwolf` with the filename `{experiment_id}.log.jsonl`.
        - `log_file_verbosity`: How verbose the logs in file should be. By default, it is the same as `verbosity`.
        - `log_file_compression`: Whether to compress the log file after the experiment.
        - `data_file`: The file to write the experimental data to during execution. If `True`, the data will be written to a file in `~/.mechwolf` with the filename `{experiment_id}.data.jsonl`.

        Returns:
        - An `Experiment` object. In a Jupyter notebook, the object yields an interactive visualization. If protocol execution fails for any reason that does not raise an error, the return type is None.

        Raises:
        - `RuntimeError`: When attempting to execute a protocol on invalid components.
        """

        # If protocol is executing, return an error
        if self.is_executing:
            raise RuntimeError("Protocol is currently running.")

        logger.info(f"Compiling protocol with dry_run = {dry_run}")
        try:
            compiled_protocol = self._compile(dry_run=bool(dry_run))
        except RuntimeError as e:
            # add an execution-specific message
            raise (RuntimeError(str(e).rstrip() + " Aborting execution..."))

        # make the user confirm if it's the real deal
        if not dry_run and not confirm:
            confirmation = input(f"Execute? [y/N]: ").lower()
            if not confirmation or confirmation[0] != "y":
                logger.critical("Aborting execution...")
                raise RuntimeError("Execution aborted by user.")

        self.is_executing = True

        # the Experiment object is going to hold all the info
        E = Experiment(
            self, compiled_protocol=compiled_protocol, verbosity=verbosity.upper()
        )
        display(E._output_widget)  # type: ignore

        # handle logging to a file
        if log_file:
            # automatically log to the mw directory
            if log_file is True:
                mw_path = Path("~/.mechwolf").expanduser()
                try:
                    mw_path.mkdir()
                except FileExistsError:
                    pass
                log_file = mw_path / Path(E.experiment_id + ".log.jsonl")

            # automatically configure a logger to persist the logs
            self._file_logger_id = logger.add(
                log_file,
                level=verbosity.upper()
                if log_file_verbosity is None
                else log_file_verbosity.upper(),
                compression=log_file_compression,
                serialize=True,
                enqueue=True,
            )
            logger.trace(f"File logger ID is {self._file_logger_id}")

            # for typing's sake
            assert isinstance(log_file, (str, os.PathLike))

            # determine the log file's path
            if log_file_compression is not None:
                self._log_file = Path(log_file)
                self._log_file = self._log_file.with_suffix(
                    self._log_file.suffix + "." + log_file_compression
                )
            else:
                self._log_file = Path(log_file)

        if data_file:
            # automatically log to the mw directory
            if data_file is True:
                mw_path = Path("~/.mechwolf").expanduser()
                try:
                    mw_path.mkdir()
                except FileExistsError:
                    pass
                E._data_file = mw_path / Path(E.experiment_id + ".data.jsonl")
            elif isinstance(data_file, (str, os.PathLike)):
                E._data_file = Path(data_file)
            else:
                raise TypeError(
                    f"Invalid type {type(data_file)} for data file."
                    "Expected str or os.PathLike (such as a pathlib.Path object)."
                )

            self._data_file = E._data_file
        logger.debug("Initiating async execution")
        if get_ipython():
            asyncio.ensure_future(main(experiment=E, dry_run=dry_run, strict=strict))
        else:
            asyncio.run(main(experiment=E, dry_run=dry_run, strict=strict))

        return E

    def clear_procedures(self) -> None:
        """
        Reset the protocol's procedures.
        """
        if not self.was_executed or self.is_executing:
            self.procedures = []
        else:
            raise RuntimeError(
                "Unable to clear the procedures of a protocol that has been executed."
            )
