import json
import os
import time
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, Optional, Union

import aiofiles
import ipywidgets as widgets
from bokeh.io import output_notebook, push_notebook, show
from bokeh.plotting import figure
from bokeh.resources import INLINE
from IPython import get_ipython
from loguru import logger
from xxhash import xxh32

from ..components import ActiveComponent, Sensor

# handle the hard issue of circular dependencies
if TYPE_CHECKING:
    from .protocol import Protocol
    from .execute import Datapoint


class Experiment(object):
    """
    Experiments contain all data from execution of a protocol.

    Arguments:
    - `protocol`: The protocol for which the experiment was conducted
    - `compiled_protocol`: The results of `protocol.compile()`.
    - `verbosity`: See `Protocol.execute` for a description of the verbosity options.

    Attributes:
    - `cancelled`: Whether the experiment was cancelled.
    - `data`: A list of `Datapoint` namedtuples from the experiment's sensors.
    - `end_time`: The Unix time of the experiment's end.
    - `executed_procedures`: A list of the procedures that were executed during the experiment.
    - `experiment_id`: The experiment's ID. By default, of the form `YYYY_MM_DD_HH_MM_SS_HASH`, where HASH is the 32-bit hexadecmial xxhash of the protocol's YAML.
    - `paused`: Whether the experiment is currently paused.
    - `start_time`: The Unix time of the experiment's start.
    """

    def __init__(
        self,
        protocol: "Protocol",
        compiled_protocol: Mapping[
            ActiveComponent,
            Iterable[Mapping[str, Union[float, str, Mapping[str, Any]]]],
        ],
        verbosity: str,
    ):
        """See the main docstring."""
        self.protocol = protocol
        self.compiled_protocol = compiled_protocol
        self.cancelled = False

        # computed values
        self.experiment_id = f'{time.strftime("%Y_%m_%d_%H_%M_%S")}_{xxh32(str(protocol.yaml())).hexdigest()}'

        # default values
        self.start_time: Optional[float] = None  # hasn't started until main() is called
        self.end_time: float
        self.data: Dict[str, List[Datapoint]] = {}
        self.executed_procedures: List[
            Dict[str, Union[float, Dict[str, Any], str, ActiveComponent]]
        ] = []

        # internal values (unstable!)
        self._charts = {}  # type: ignore
        self._graphs_shown = False
        self._sensors = [c for c in self.compiled_protocol if isinstance(c, Sensor)]
        self._sensors.reverse()
        self._device_name_to_unit = {c.name: c._unit for c in self._sensors}
        self._sensor_names: List[str] = [s.name for s in self._sensors]
        self._transformed_data: Dict[str, Dict[str, List[Datapoint]]] = {
            s: {"datapoints": [], "timestamps": []} for s in self._sensor_names
        }
        self._bound_logger = None
        self._plot_height = 300
        self._paused = False
        self._data_file: Optional[os.PathLike] = None

        # don't do any of the UI stuff if not in the notebook
        # if get_ipython() is None:
        #     return

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
            "Apparatus Name": self.protocol.apparatus.name,
            "Protocol name": self.protocol.name,
        }.items():
            metadata += f"<li>{k}: {v}</li>"
        metadata += "</ul>"

        # create the output tab widget with a log tab
        self._tab = widgets.Tab()
        self._log_widget = widgets.Output()
        self._tab.children = (widgets.HTML(value=metadata), self._log_widget)
        self._tab.set_title(0, "Metadata")
        self._tab.set_title(1, "Log")

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

        self._output_widget = widgets.VBox(
            [
                widgets.HTML(value=f"<h3>Experiment {self.experiment_id}</h3>"),
                widgets.HBox([self._pause_button, self._stop_button]),
                self._tab,
            ]
        )

        def _log(x):
            with self._log_widget:  # the log
                pad_length = (
                    len(str(int(self.protocol._inferred_duration))) + 4
                )  # .xxx in floats
                if self.start_time is not None:
                    print(
                        f"({time.time() - self.start_time:0{pad_length}.3f}s) {x.rstrip()}"
                    )
                else:
                    print(f"({'setup': ^{pad_length+1}}) " + x.rstrip())

        # don't enqueue since it breaks the graphing
        self._bound_logger = logger.add(
            lambda x: _log(x),
            level=verbosity,
            colorize=True,
            format="{level.icon} {message}",
        )

    def __str__(self):
        return f"Experiment {self.experiment_id}"

    def __repr__(self):
        return f"<Experiment {self.experiment_id}>"

    async def update(self, device: str, datapoint):

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
        self.cancelled = True

    def _on_pause_clicked(self, b):
        self.paused = not self.paused

    @property
    def paused(self):
        return self._paused

    @paused.setter
    def paused(self, paused):
        if paused:
            logger.warning(f"Paused execution.")
        else:
            logger.warning(f"Resumed execution.")
        self._paused = paused
        self._pause_button.description = "Resume" if paused else "Pause"
        self._pause_button.button_style = "success" if paused else ""
        self._pause_button.icon = "play" if paused else "pause"
