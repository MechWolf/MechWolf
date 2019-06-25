import time
from uuid import uuid1
from warnings import warn

from bokeh.io import output_notebook, push_notebook, show
from bokeh.plotting import figure


class Experiment(object):
    """
        Experiments contain all data from execution of a protocol.
    """

    def __init__(self, protocol):
        self.experiment_id = f'{time.strftime("%Y_%m_%d_%H_%M_%S")}_{uuid1()}'

        self.protocol = protocol
        self.start_time = None  # the experiment hasn't started until main() is called
        self.end_time = None
        self.data = {}
        self.executed_procedures = []

        self._charts = {}
        self._transformed_data = {}

    def _transform_data(self, device):
        return {
            "datapoints": [datapoint.datapoint for datapoint in self.data[device]],
            "timestamps": [
                datapoint.timestamp - self.start_time for datapoint in self.data[device]
            ],
        }

    def __repr__(self):
        return f"<Experiment {self.experiment_id}>"

    def __str__(self):
        return f"Experiment {self.experiment_id}"

    def visualize(self):
        try:
            get_ipython  # noqa
        except NameError:
            warn(
                "Visualization of Experiment objects is only supported inside Jupyter notebooks. Skipping..."
            )
            return False
        output_notebook()

        for device in self.data:
            self._transformed_data[device] = self._transform_data(device)
            p = figure(title=f"{device} data", plot_height=300, plot_width=600)
            r = p.line(
                source=self._transformed_data[device],
                x="timestamps",
                y="datapoints",
                color="#2222aa",
                line_width=3,
            )
            target = show(p, notebook_handle=True)
            # Register chart for continuous updating
            self._charts[device] = (target, r)

    def update(self, device, datapoint):
        # If a chart has been registered to the device, update it.
        if device not in self.data:
            self.data[device] = []
        self.data[device].append(datapoint)

        if device in self._transformed_data:
            target, r = self._charts[device]
            self._transformed_data[device]["datapoints"].append(datapoint.datapoint)
            self._transformed_data[device]["timestamps"].append(
                datapoint.timestamp - self.start_time
            )
            r.data_source.data["datapoints"] = self._transformed_data[device][
                "datapoints"
            ]
            r.data_source.data["timestamps"] = self._transformed_data[device][
                "timestamps"
            ]
            push_notebook(handle=target)
