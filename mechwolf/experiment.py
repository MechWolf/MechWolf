import time

import ipywidgets as widgets
from bokeh.io import output_notebook, push_notebook, show
from bokeh.plotting import figure
from bokeh.resources import INLINE
from loguru import logger
from xxhash import xxh32

from .components import Sensor

try:
    get_ipython  # noqa
    in_ipython = True
except NameError:
    in_ipython = False


class Experiment(object):
    """
        Experiments contain all data from execution of a protocol.
    """

    def __init__(self, protocol, compiled_protocol: dict, verbosity: str):
        self.protocol = protocol
        self.compiled_protocol = compiled_protocol

        # computed values
        self.experiment_id = f'{time.strftime("%Y_%m_%d_%H_%M_%S")}_{xxh32(str(protocol.yaml())).hexdigest()}'

        # default values
        self.start_time = None  # the experiment hasn't started until main() is called
        self.end_time = None
        self.data = {}
        self.executed_procedures = []
        self._plot_height = 300

        # internal values (unstable!)
        self._charts = {}
        self._graphs_shown = False
        self._sensors = [c for c in self.compiled_protocol if isinstance(c, Sensor)][
            ::-1
        ]  # reverse the list so the accordion is in order
        self._device_name_to_unit = {c.name: c._unit for c in self._sensors}
        self._sensor_names = [s.name for s in self._sensors]
        self._transformed_data = {
            s: {"datapoints": [], "timestamps": []} for s in self._sensor_names
        }
        self._bound_logger = None

        # create a nice, pretty HTML string wth the metadata
        metadata = "<ul>"
        for k, v in {
            "Protocol name": self.protocol.name,
            "Start time": self.start_time,
        }.items():
            metadata += f"<li>{k}: {v}</li>"
        metadata += "</ul>"

        # create the output tab widget with its children
        self._tab = widgets.Tab()
        self._tab.children = [widgets.HTML(value=metadata), widgets.Output()]
        self._tab.set_title(0, "Metadata")
        self._tab.set_title(1, "Log")
        if self._sensors:
            self._tab.children = list(self._tab.children) + [
                widgets.Accordion(children=[widgets.Output() for s in self._sensors])
            ]
            self._tab.set_title(2, "Sensors")
            for i, sensor in enumerate(self._sensors):
                self._tab.children[2].set_title(i, sensor.name)
        self._output_widget = widgets.VBox(
            [widgets.HTML(value=f"<h3>Experiment {self.experiment_id}</h3>"), self._tab]
        )

        def log(x):
            with self._output_widget.children[1].children[1]:  # the log
                pad_length = (
                    len(str(int(self.protocol._inferred_duration))) + 4
                )  # .xxx in floats
                if self.start_time is not None:
                    print(
                        f"({time.time() - self.start_time:0{pad_length}.3f}s) {x.rstrip()}"
                    )
                else:
                    print(f"({'setup': ^{pad_length+1}}) " + x.rstrip())

        self._bound_logger = logger.add(
            lambda x: log(x),
            level=verbosity,
            colorize=True,
            format="{level.icon} {message}",
        )
        logger.level("SUCCESS", icon="✅")
        logger.level("ERROR", icon="❌")
        logger.level("TRACE", icon="🔍")

    def __str__(self):
        return f"Experiment {self.experiment_id}"

    def __repr__(self):
        return f"<Experiment {self.experiment_id}>"

    def update(self, device: str, datapoint):

        # If a chart has been registered to the device, update it.
        if device not in self.data:
            self.data[device] = []
        self.data[device].append(datapoint)

        if not in_ipython:
            return

        if not self._graphs_shown:
            logger.debug("Graphs not shown. Initializing...")
            for i, sensor in enumerate(self._sensor_names):
                logger.trace(f"Initializing graph #{i+1} for {sensor}")

                # bind the height of the graph to the selected plot height
                self._output_widget.children[1].children[2].children[
                    i
                ].layout.height = f"{self._plot_height}px"
                with self._output_widget.children[1].children[2].children[i]:

                    # create the figure object
                    p = figure(
                        title=f"{sensor} data",
                        plot_height=self._plot_height,
                        plot_width=600,
                    )
                    r = p.line(
                        source=self._transformed_data[sensor],
                        x="timestamps",
                        y="datapoints",
                        color="#2222aa",
                        line_width=3,
                    )
                    p.xaxis.axis_label = "Experiment elapsed time (seconds)"
                    p.yaxis.axis_label = self._device_name_to_unit[sensor]

                    # since we're in the with-statement, this will show up in the accordion
                    output_notebook(resources=INLINE, hide_banner=True)
                    target = show(p, notebook_handle=True)

                    # save the target and plot for later updating
                    self._charts[sensor] = (target, r)
                logger.trace(f"Sucessfully initialized graph {i}")
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
