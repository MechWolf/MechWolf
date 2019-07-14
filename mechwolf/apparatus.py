from collections import namedtuple
from typing import Iterable, Optional, Union
from warnings import warn

import networkx as nx
from graphviz import Digraph
from IPython.display import HTML, Markdown
from mistune import markdown
from terminaltables import AsciiTable, GithubFlavoredMarkdownTable

from . import ureg
from .components import ActiveComponent, Component, Tube, Valve, Vessel

Connection = namedtuple("Connection", ["from_component", "to_component", "tube"])


class Apparatus(object):
    """
    A unique network of components.

    ::: tip Note
    The same components may be organized into multiple distinct apparatuses, depending on the connections between them.
    :::

    Attributes:
    - `network`: A list of tuples in the form `(from_component, to_component, tube)` describing the configuration of the apparatus.
    - `components` (set): The components that make up the apparatus.

    See also the arguments of `__init__()` for more attributes.
    """

    _id_counter = 0

    def __init__(self, name: Optional[str] = None, description: Optional[str] = None):
        """
        # Arguments
        - `name`: The name of the apparatus. Defaults to "Apparatus_X" where *X* is apparatus count. This should be short and sweet.
        - `description`: A description of the apparatus. Can be as long and wordy as you want.
        """
        self.network = []
        self.components = set()
        # if given a name, then name the apparatus, else default to a sequential name
        if name is not None:
            self.name = name
        else:
            self.name = "Apparatus_" + str(Apparatus._id_counter)
            Apparatus._id_counter += 1
        self.description = description

    def __repr__(self):
        return f"<Apparatus {self.name}>"

    def __str__(self):
        return f"Apparatus {self.name}"

    @property
    def _active_components(self) -> set:
        return {x for x in self.components if isinstance(x, ActiveComponent)}

    def _add_single(
        self, from_component: Component, to_component: Component, tube: Tube
    ) -> None:
        """Adds a single connection to the apparatus.

        For args, see add().
        """
        if not issubclass(from_component.__class__, Component):
            raise ValueError("From component must be a subclass of Component")
        if not issubclass(to_component.__class__, Component):
            raise ValueError("To component must be a subclass of Component")
        if not issubclass(tube.__class__, Tube):
            raise ValueError("Tube must be an instance of Tube")

        self.network.append(
            Connection(
                from_component=from_component, to_component=to_component, tube=tube
            )
        )
        self.components.update([from_component, to_component])

    def add(
        self,
        from_component: Union[Component, Iterable],
        to_component: Component,
        tube: Tube,
    ) -> None:
        """
        Adds connections to the apparatus.

        # Arguments
        - `from_component`: The `Component` from which the flow is originating. If an iterable, all items in the iterable will be connected to the same component.
        - `to_component`: The `Component` where the flow is going.
        - `tube`: `Tube` that connects the components.

        # Raises
        - `ValueError`: When the connection being added is invalid.
        """

        if isinstance(from_component, Iterable):
            for component in from_component:
                self._add_single(component, to_component, tube)
        else:
            self._add_single(from_component, to_component, tube)

    def visualize(
        self,
        title: bool = True,
        label_tubes: bool = False,
        describe_vessels: bool = False,
        node_attr: dict = {},
        edge_attr: dict = {},
        graph_attr: dict = dict(splines="ortho"),
        file_format: str = "pdf",
        filename: Optional[str] = None,
    ) -> Optional[Digraph]:
        """
        Generates a visualization of the graph of an apparatus.

        For full list of acceptable Graphviz attributes for see [the graphviz.org docs](http://www.graphviz.org/doc/info/attrs.html) and [its Python API's docs](http://graphviz.readthedocs.io/en/stable/manual.html#attributes).

        # Arguments
        - `title`: Whether to show the title in the output. Defaults to True.
        - `label_tubes`: Whether to label the tubes between components with the length, inner diameter, and outer diameter.
        - `describe_vessels`: Whether to display the names or content descriptions of `Vessel` components.
        - `node_attr`: Controls the appearance of the nodes of the graph. Must be of the form `{"attribute": "value"}`.
        - `edge_attr`: Controls the appearance of the edges of the graph. Must be of the form `{"attribute": "value"}`.
        - `graph_attr`: Controls the appearance of the graph. Must be of the form `{"attribute": "value"}`. Defaults to orthogonal splines and a node separation of 1
        - `file_format`: The output format of the graph, either "pdf" or "png".
        - `filename`: The name of the output file. Defaults to the name of the apparatus.

        # Raises
        - `ImportError`: When the visualization package is not installed.
        """
        f = Digraph(
            name=self.name,
            node_attr=node_attr,
            edge_attr=edge_attr,
            graph_attr=graph_attr,
            format=file_format,
            filename=filename,
        )

        # go from left to right adding components and their tubing connections
        f.attr(rankdir="LR")

        for component in sorted(list(self.components), key=lambda x: x.name):
            f.attr("node", shape=component._visualization_shape)
            f.node(
                component.description
                if isinstance(component, Vessel) and describe_vessels
                else component.name
            )

        for c in self.network:
            tube = c.tube
            tube_label = (
                f"Length {tube.length}\nID {tube.ID}\nOD {tube.OD}"
                if label_tubes
                else ""
            )
            f.edge(
                c.from_component.description
                if isinstance(c.from_component, Vessel) and describe_vessels
                else c.from_component.name,
                c.to_component.description
                if isinstance(c.to_component, Vessel) and describe_vessels
                else c.to_component.name,
                label=tube_label,
            )

        # show the title of the graph
        if title:
            title = title if not title else self.name
            f.attr(label=title)

        try:
            get_ipython()
            return f
        except NameError:
            f.view(cleanup=True)

    def summarize(self, style: str = "gfm") -> Optional[HTML]:
        """
        Prints a summary table of the apparatus.

        # Arguments
        - `style`: Either `gfm` for GitHub-flavored Markdown or `ascii`. If equal to `gfm` and in a Jupyter notebook, returns a rendered HTML version of the GFM table.

        # Returns
        In Jupyter, a nice HTML table. Otherwise, the output is printed to the terminal.
        """

        if style == "ascii":
            tableStyle = AsciiTable
        else:
            tableStyle = GithubFlavoredMarkdownTable

        # create a components table
        summary = [["Name", "Type"]]  # header rows of components table
        for component in list(self.components):
            if not isinstance(component, Vessel):
                summary.append([component.name, component.__class__.__name__])
            else:
                # we want to know what's actually in the vessel
                summary.append([component.description, component.__class__.__name__])

        # generate the components table
        components_table = tableStyle(summary)
        components_table.title = "Components"

        # summarize the tubing
        summary = [
            [
                "From",
                "To",
                "Length",
                "Inner Diameter",
                "Outer Diameter",
                "Volume",
                "Material",
            ]
        ]  # header row

        # store and calculate the computed totals for tubing
        total_length = 0 * ureg.mm
        total_volume = 0 * ureg.ml
        for connection in self.network:
            total_length += connection.tube.length
            total_volume += connection.tube.volume

            summary.append(
                [
                    connection.from_component.name,
                    connection.to_component.name,
                    round(connection.tube.length, 4),
                    round(connection.tube.ID, 4),
                    round(connection.tube.OD, 4),
                    round(connection.tube.volume.to("ml"), 4),
                    connection.tube.material,
                ]
            )
        summary.append(
            [
                "",
                "**Total**" if style == "gfm" else "Total",
                round(total_length, 4),
                "n/a",
                "n/a",
                round(total_volume.to("ml"), 4),
                "n/a",
            ]
        )  # footer row

        # generate the tubing table
        tubing_table = tableStyle(summary)
        tubing_table.title = "Tubing"
        tubing_table.inner_footing_row_border = "True"

        try:
            get_ipython
            if style == "gfm":
                html = (
                    f"<h3>{components_table.title}</h3>"
                    f"{markdown(components_table.table)}"
                    f"<h3>{tubing_table.title}</h3>{markdown(tubing_table.table)}"
                )
                return HTML(html)
        except NameError:
            pass
        print("Components")
        print(components_table.table)
        print("\nTubing")
        print(tubing_table.table)

    def validate(self) -> bool:
        """
        Checks that the apparatus is valid.

        ::: tip
        Calling this function yourself is likely unnecessary because the `Protocol` class calls it upon instantiation.
        :::

        # Returns
        Whether the apparatus is valid.
        """

        # make sure that all of the components are connected
        G = nx.Graph()  # convert the network to an undirected NetworkX graph
        G.add_edges_from([(c.from_component, c.to_component) for c in self.network])
        if not nx.is_connected(G):
            warn("Not all components connected.")
            return False

        # valve checking
        valves = [x for x in self.components if isinstance(x, Valve)]
        for valve in valves:

            # ensure that valve's mapping components are part of apparatus
            for component in valve.mapping.keys():
                if component not in self.components:
                    warn(
                        f"Invalid mapping for Valve {valve}. "
                        f"{component} has not been added to {self.name}"
                    )
                    return False

            # TODO: make this check work again with SISO, SIMO, MISO, and MIMO valves.
            # # no more than one output from a valve (might have to change this)
            # if len([x for x in self.network if x.from_component is valve]) != 1:
            #     warn(f"Valve {valve} has multiple outputs.")
            #     return False
            #
            # make sure valve's mapping is complete
            # non_mapped_components = [
            #     connection.from_component
            #     for connection in self.network
            #     if connection.to_component == valve
            #     and valve.mapping.get(connection.from_component.name) is None
            # ]
            # if non_mapped_components:
            #     warn(
            #         f"Valve {valve} has incomplete mapping."
            #         f" No mapping for {non_mapped_components}"
            #     )
            #     return False

        return True

    def describe(self) -> Union[str, Markdown]:
        """
        Generates a human-readable description of the apparatus.

        # Returns
        - `str`: A description of apparatus. When in Jupyter, this string is wrapped in a `IPython.display.Markdown` object for nicer display.

        # Raises
        - `RuntimeError`: When a component cannot be described.
        """

        def _description(element, capitalize=False):
            """takes a component and converts it to a string description"""
            if issubclass(element.__class__, Vessel):
                return f"{'A' if capitalize else 'a'} vessel containing {element.description}"
            elif issubclass(element.__class__, Component):
                return element.__class__.__name__ + " " + element.name
            else:
                raise RuntimeError(
                    f"{element} cannot be described."
                    " If you're seeing this message, something *very* wrong has happened."
                )

        result = ""

        # iterate over the network and describe the connections
        for connection in self.network:
            from_component, to_component, tube = (
                _description(connection.from_component, capitalize=True),
                _description(connection.to_component),
                connection.tube,
            )
            result += (
                f"{from_component} was connected to"
                f" {to_component} using {connection[2].material}"
                f" tubing (length {tube.length}, ID {tube.ID}, OD {tube.OD}). "
            )
        try:
            get_ipython
            return Markdown(result)
        except NameError:
            pass
        return result
