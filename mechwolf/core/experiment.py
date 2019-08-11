import asyncio
import json
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from warnings import warn

import aiofiles
import ipywidgets as widgets
from bokeh.io import output_notebook, push_notebook, show
from bokeh.plotting import figure
from bokeh.resources import INLINE
from IPython import get_ipython
from IPython.display import display
from loguru import logger
from xxhash import xxh32

from ..components import ActiveComponent, Sensor
from .execute import main

# handle the hard issue of circular dependencies
if TYPE_CHECKING:
    from .protocol import Protocol
    from .execute import Datapoint


class Experiment(object):
    """
    Experiments contain all data from execution of a protocol.

    Arguments:
    - `protocol`: The protocol for which the experiment was conducted
    - `compiled_protocol`: The results of `protocol._compile()`.
    - `verbosity`: See `Protocol.execute` for a description of the verbosity options.
    - `dry_run`: Whether the experiment is a dry run and, if so, by what factor it is sped up by.

    Attributes:
    - `cancelled`: Whether the experiment was cancelled.
    - `compiled_protocol`: The results of `protocol._compile()`.
    - `data`: A list of `Datapoint` namedtuples from the experiment's sensors.
    - `dry_run`: Whether the experiment is a dry run and, if so, by what factor it is sped up by.
    - `end_time`: The Unix time of the experiment's end.
    - `executed_procedures`: A list of the procedures that were executed during the experiment.
    - `experiment_id`: The experiment's ID. By default, of the form `YYYY_MM_DD_HH_MM_SS_HASH`, where HASH is the 32-bit hexadecmial xxhash of the protocol's YAML.
    - `paused`: Whether the experiment is currently paused.
    - `protocol`: The protocol for which the experiment was conducted
    - `start_time`: The Unix time of the experiment's start.
    - `verbosity`: See `Protocol.execute` for a description of the verbosity options.
    """

    def __init__(self, protocol: "Protocol"):
        # args
        self.apparatus = protocol.apparatus
        self.protocol = protocol

        # computed values
        self.experiment_id: Optional[str] = None

        # default values
        self.dry_run: Union[bool, int]
        self.start_time: float  # hasn't started until main() is called
        self.created_time = time.time()  # when the object was created (might be diff)
        self.end_time: float
        self.data: Dict[str, List[Datapoint]] = {}
        self.cancelled = False
        self.was_executed = False
        self.executed_procedures: List[
            Dict[str, Union[float, Dict[str, Any], str, ActiveComponent]]
        ] = []

        # internal values (unstable!)
        _local_time = time.localtime(self.created_time)
        self._created_time_local: str = time.strftime("%Y_%m_%d_%H_%M_%S", _local_time)
        self._charts = {}  # type: ignore
        self._graphs_shown = False
        self._sensors = self.apparatus[Sensor]
        self._sensors.reverse()
        self._device_name_to_unit = {c.name: c._unit for c in self._sensors}
        self._sensor_names: List[str] = [s.name for s in self._sensors]
        self._bound_logger = None
        self._plot_height = 300
        self._is_executing = False
        self._paused = False
        self._pause_times: List[Dict[str, float]] = []
        self._end_loop = False  # when to stop monitoring the buttons
        self._file_logger_id: Optional[int] = None
        self._log_file: Optional[Path] = None
        self._data_file: Optional[Path] = None
        self._transformed_data: Dict[str, Dict[str, List[Datapoint]]] = {
            s: {"datapoints": [], "timestamps": []} for s in self._sensor_names
        }

    def __str__(self):
        return f"Experiment {self.experiment_id}"

    def __repr__(self):
        return f"<Experiment {self.experiment_id}>"

    async def _update(self, device: str, datapoint):

        # If a chart has been registered to the device, update it.
        if device not in self.data:
            self.data[device] = []
        self.data[device].append(datapoint)

        if self._data_file is not None:
            line = json.dumps(
                {
                    "device": device,
                    "timestamp": datapoint.timestamp,
                    "experiment_elapsed_time": datapoint.experiment_elapsed_time,
                    "data": datapoint.data,
                    "unit": self.protocol.apparatus[device]._unit,
                }
            )
            async with aiofiles.open(self._data_file, "a+") as f:
                await f.write(line + "\n")

        if get_ipython() is None:
            return

        if not self._graphs_shown:
            logger.debug("Graphs not shown. Initializing...")
            for sensor, output in self._sensor_outputs.items():
                logger.trace(f"Initializing graph for {sensor}")

                # bind the height of the graph to the selected plot height
                output.layout.height = f"{self._plot_height}px"

                with output:
                    # create the figure object
                    p = figure(
                        title=f"{sensor} data",
                        plot_height=self._plot_height,
                        plot_width=600,
                    )
                    r = p.line(
                        source=self._transformed_data[sensor.name],
                        x="timestamps",
                        y="datapoints",
                        color="#2222aa",
                        line_width=3,
                    )
                    p.xaxis.axis_label = "Experiment elapsed time (seconds)"
                    p.yaxis.axis_label = self._device_name_to_unit[sensor.name]

                    # since we're in the with-statement, this will show up in the accordion
                    output_notebook(resources=INLINE, hide_banner=True)
                    target = show(p, notebook_handle=True)

                    # save the target and plot for later updating
                    self._charts[sensor.name] = (target, r)
                logger.trace(f"Sucessfully initialized graph for {sensor.name}")
            logger.trace("All graphs successfully initialized")
            self._graphs_shown = True

        if device in self._transformed_data:
            target, r = self._charts[device]
            self._transformed_data[device]["datapoints"].append(datapoint.data)
            self._transformed_data[device]["timestamps"].append(
                datapoint.experiment_elapsed_time
            )
            r.data_source.data["datapoints"] = self._transformed_data[device][
                "datapoints"
            ]
            r.data_source.data["timestamps"] = self._transformed_data[device][
                "timestamps"
            ]
            push_notebook(handle=target)

    def _on_stop_clicked(self, b):
        logger.debug("Stop button pressed.")
        self.cancelled = True

    def _on_pause_clicked(self, b):
        self.paused = not self.paused

    @property
    def _total_paused_duration(self) -> float:
        """Calculate the total amount of time the experiment was paused for."""
        duration = 0.0
        for pause in self._pause_times:
            if "stop" in pause:
                duration += pause["stop"] - pause["start"]
        return duration

    def _execute(
        self,
        dry_run: Union[bool, int],
        verbosity: str,
        confirm: bool,
        strict: bool,
        log_file: Union[str, bool, os.PathLike, None],
        log_file_verbosity: Optional[str],
        log_file_compression: Optional[str],
        data_file: Union[str, bool, os.PathLike, None],
    ):
        self.dry_run = dry_run

        # make the user confirm if it's the real deal
        if not self.dry_run and not confirm:
            confirmation = input(f"Execute? [y/N]: ").lower()
            if not confirmation or confirmation[0] != "y":
                logger.critical("Aborting execution...")
                raise RuntimeError("Execution aborted by user.")

        self._compiled_protocol = self.protocol._compile(dry_run=bool(dry_run))

        # now that we're ready to start, create the time and ID attributes
        protocol_hash: str = xxh32(str(self.protocol.yaml())).hexdigest()
        self.experiment_id = f"{self._created_time_local}_{protocol_hash}"

        # handle logging to a file
        if log_file:
            # automatically log to the mw directory
            if log_file is True:
                mw_path = Path("~/.mechwolf").expanduser()
                try:
                    mw_path.mkdir()
                except FileExistsError:
                    pass
                log_file = mw_path / Path(self.experiment_id + ".log.jsonl")

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
                self._data_file = mw_path / Path(self.experiment_id + ".data.jsonl")
            elif isinstance(data_file, (str, os.PathLike)):
                self._data_file = Path(data_file)
            else:
                raise TypeError(
                    f"Invalid type {type(data_file)} for data file."
                    "Expected str or os.PathLike (such as a pathlib.Path object)."
                )

            self._data_file = self._data_file

        if get_ipython():
            self._display(verbosity=verbosity.upper(), strict=strict)
            asyncio.ensure_future(main(experiment=self, dry_run=dry_run, strict=strict))
        else:
            asyncio.run(main(experiment=self, dry_run=dry_run, strict=strict))

    def _display(self, verbosity: str, strict: bool):

        # create pause button
        self._pause_button = widgets.Button(description="Pause", icon="pause")
        self._pause_button.on_click(self._on_pause_clicked)

        # create a stop button
        self._stop_button = widgets.Button(
            description="Stop", button_style="danger", icon="stop"
        )
        self._stop_button.on_click(self._on_stop_clicked)

        # create a nice, pretty HTML string wth the metadata
        metadata = "<ul>"
        for k, v in {
            "Apparatus": self.apparatus.name,
            "Protocol": self.protocol.name,
            "Description": self.protocol.description,
            "Start time": time.ctime(self.created_time),
            "Expected completion": time.ctime(
                self.created_time + self.protocol._inferred_duration
            ),
            "Procedure count": sum([len(x) for x in self._compiled_protocol.values()]),
            "Abort on error": strict,
            "Log file": self._log_file.absolute() if self._log_file else None,
            "Data file": self._data_file.absolute() if self._data_file else None,
        }.items():
            if not v:
                continue
            metadata += f"<li><b>{k}:</b> {v}</li>"
        metadata += "</ul>"

        # create the output tab widget with a log tab
        self._tab = widgets.Tab()
        self._log_widget = widgets.Output()
        self._tab.children = (self._log_widget, widgets.HTML(value=metadata))
        self._tab.set_title(0, "Log")
        self._tab.set_title(1, "Metadata")

        if self._sensors:
            self._sensor_outputs = {s: widgets.Output() for s in self._sensors}

            self._accordion = widgets.Accordion(
                children=tuple(self._sensor_outputs.values())
            )
            self._tab.children = tuple(list(self._tab.children) + [self._accordion])
            self._tab.set_title(2, "Sensors")

            # we know that the accordion will line up with the dict since dict order
            # is preserved in Python 3.7+
            for i, sensor in enumerate(self._sensor_outputs):
                self._accordion.set_title(i, sensor.name)

        # decide whether to show a pause button
        buttons = [self._stop_button]
        if type(self.dry_run) != int:
            buttons.insert(0, self._pause_button)

        self._output_widget = widgets.VBox(
            [
                widgets.HTML(value=f"<h3>Experiment {self.experiment_id}</h3>"),
                widgets.HBox(buttons),
                self._tab,
            ]
        )

        def _log(x):
            with self._log_widget:  # the log
                # .xxx in floats
                pad_length = len(str(int(self.protocol._inferred_duration))) + 4
                # we don't (cleanup) to look weird, so pad to at least its length
                pad_length = max((pad_length, len("cleanup")))

                if self.is_executing and not self.was_executed:
                    elapsed_time = f"{time.time() - self.start_time:0{pad_length}.3f}"
                    print(f"({elapsed_time}) {x.rstrip()}")
                elif self.was_executed:
                    print(f"({'cleanup'.center(pad_length)}) {x.rstrip()}")
                else:
                    print(f"({'setup'.center(pad_length)}) " + x.rstrip())

        # don't enqueue since it breaks the graphing
        self._bound_logger = logger.add(
            lambda x: _log(x),
            level=verbosity,
            colorize=True,
            format="{level.icon} {message}",
        )

        display(self._output_widget)

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
        logger.trace(f"{repr(self)}.is_executing is now {is_executing}")
        self._is_executing = is_executing

    @property
    def paused(self):
        return self._paused

    @paused.setter
    def paused(self, paused):

        # pausing a sped up dry run is meaningless
        if type(self.dry_run) == int:
            warn("Pausing a speed run is not supported. This will have no effect.")

        # issue a warning if the user overuses the pause button
        if len(self._pause_times) >= 3:
            logger.warning("Pausing repeatedly may adversely affect protocol timing.")

        if paused and not self._paused:
            logger.warning(f"Paused execution.")
            self._pause_times.append(dict(start=time.time()))
        elif not paused and self._paused:
            self._pause_times[-1]["stop"] = time.time()
            logger.warning(f"Resumed execution.")
        self._paused = paused

        # control the pause button
        self._pause_button.description = "Resume" if paused else "Pause"
        self._pause_button.button_style = "success" if paused else ""
        self._pause_button.icon = "play" if paused else "pause"
