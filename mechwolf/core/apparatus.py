from collections import namedtuple
from typing import Iterable, List, Mapping, Optional, Set, Union
from warnings import warn

import networkx as nx
from graphviz import Digraph
from IPython import get_ipython
from IPython.display import Markdown
from terminaltables import AsciiTable, GithubFlavoredMarkdownTable

from .. import _ureg
from ..components import Component, Tube, Valve, Vessel

Connection = namedtuple("Connection", ["from_component", "to_component", "tube"])


class Apparatus(object):
    """
    A unique network of components.

    ::: tip Note
    The same components may be organized into multiple distinct apparatuses, depending on the connections between them.
    :::

    Arguments:
    - `name`: The name of the apparatus. Defaults to "Apparatus_X" where *X* is apparatus count. This should be short and sweet.
    - `description`: A description of the apparatus. Can be as long and wordy as you want.

    Attributes:
    - `components`: A set containing the components that make up the apparatus.
    - `description`: A description of the apparatus. Can be as long and wordy as you want.
    - `name`: The name of the apparatus. Defaults to "Apparatus_X" where *X* is apparatus count. This should be short and sweet.
    - `network`: A list of tuples in the form `(from_component, to_component, tube)` describing the configuration of the apparatus.
    """

    _id_counter = 0

    def __init__(self, name: Optional[str] = None, description: Optional[str] = None):
        """
        See the main docstring.
        """
        self.network: List[Connection] = []
        self.components: Set[Component] = set()
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

    def __getitem__(self, item):
        # when you pass a class
        if isinstance(item, type):
            return [
                component
                for component in self.components
                if isinstance(component, item)
            ]
        elif isinstance(item, str):
            try:
                return [
                    component for component in self.components if component.name == item
                ][0]
            except IndexError:
                raise KeyError(f"No component named '{item}' in {repr(self)}.")

        # a shorthand way to check if a component is in the apparatus
        elif isinstance(item, Component):
            if item in self.components:
                return item
            else:
                raise KeyError(f"{repr(item)} is not in {repr(self)}.")

    def _add_single(
        self, from_component: Component, to_component: Component, tube: Tube
    ) -> None:
        """Adds a single connection to the apparatus.

        For args, see add().
        """
        if not isinstance(from_component, Component):
            raise ValueError("From component must be an instance of Component")
        if not isinstance(to_component, Component):
            raise ValueError("To component must be an instance of Component")
        if not isinstance(tube, Tube):
            raise ValueError("Tube must be an instance of Tube")

        # check for duplicate names
        try:
            if self[from_component.name] is not from_component:
                raise ValueError(f"Component {from_component} has duplicated name")
        except KeyError:
            pass
        try:
            if self[to_component.name] is not to_component:
                raise ValueError(f"Component {to_component} has duplicated name")
        except KeyError:
            pass

        if (
            Connection(
                from_component=from_component, to_component=to_component, tube=tube
            )
            in self.network
        ):
            warn(
                f"Duplicate connection from {from_component} to {to_component} omitted."
            )
            return

        self.network.append(
            Connection(
                from_component=from_component, to_component=to_component, tube=tube
            )
        )
        self.components.update([from_component, to_component])

    def add(
        self,
        from_component: Union[Component, Iterable[Component]],
        to_component: Union[Component, Iterable[Component]],
        tube: Tube,
    ) -> None:
        """
        Adds connections to the apparatus.
        If both `from_component` and `to_component` are iterables, then their Cartesian product will be added to the apparatus.

        Arguments:
        - `from_component`: The `Component` from which the flow is originating. If an iterable, all items in the iterable will be connected to the same component.
        - `to_component`: The `Component` where the flow is going. If an iterable, all items in the iterable will be connected to the same component.
        - `tube`: `Tube` that connects the components.

        Raises:
        - `ValueError`: When the connection being added is invalid.
        """

        # the cartesian product
        if isinstance(from_component, Iterable) and isinstance(to_component, Iterable):
            for _from_component in from_component:
                for _to_component in to_component:
                    self._add_single(_from_component, _to_component, tube)

        # multiple from components, one to component
        elif isinstance(from_component, Iterable) and not isinstance(
            to_component, Iterable
        ):
            for _from_component in from_component:
                self._add_single(_from_component, to_component, tube)

        # multiple to components, one from component
        elif isinstance(to_component, Iterable) and not isinstance(
            from_component, Iterable
        ):
            for _to_component in to_component:
                self._add_single(from_component, _to_component, tube)

        # one to and one from component
        elif not isinstance(to_component, Iterable) and not isinstance(
            from_component, Iterable
        ):
            self._add_single(from_component, to_component, tube)

    def visualize(
        self,
        title: Union[bool, str] = True,
        label_tubes: bool = False,
        describe_vessels: bool = False,
        rankdir: str = "LR",
        node_attr: Optional[Mapping[str, str]] = None,
        edge_attr: Optional[Mapping[str, str]] = None,
        graph_attr: Optional[Mapping[str, str]] = None,
        file_format: str = "pdf",
        filename: Optional[str] = None,
        **kwargs,
    ) -> Optional[Digraph]:
        """
        Generates a visualization of an apparatus's network graph.

        For full list of acceptable Graphviz attributes, see [the graphviz.org docs](http://www.graphviz.org/doc/info/attrs.html) and [its Python API's docs](http://graphviz.readthedocs.io/en/stable/manual.html#attributes).

        Arguments:
        - `describe_vessels`: Whether to display the names or content descriptions of `Vessel` components.
        - `edge_attr`: Controls the appearance of the edges (tubes) of the Apparatus. Must be of the form `{"attribute": "value"}`.
        - `file_format`: The output format of the graph, either "pdf" or "png".
        - `filename`: The name of the output file. Defaults to the name of the apparatus.
        - `graph_attr`: Controls the appearance of the Apparatus. Must be of the form `{"attribute": "value"}`. To get orthogonal splines (*i.e.* edges with sharp corners), pass `splines="ortho"`. To increase the separation between components, set `nodesep = "0.5"` or similar.
        - `label_tubes`: Whether to label the tubes between components with the length, inner diameter, and outer diameter.
        - `node_attr`: Controls the appearance of the nodes (components) of the Apparatus. Must be of the form `{"attribute": "value"}`.
        - `rankdir`: The direction of the graph. Use `LR` for left to right and `TD` for top down.
        - `title`: Whether to show the title in the output. Defaults to True. If a string, the title to use for the output.
        """
        f = Digraph(
            name=self.name,
            node_attr=node_attr,
            edge_attr=edge_attr,
            graph_attr=graph_attr if graph_attr is not None else {},
            format=file_format,
            filename=filename,
            **kwargs,
        )

        # go from left to right adding components and their tubing connections
        f.attr(rankdir=rankdir)

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
            title = title if isinstance(title, str) else self.name
            f.attr(label=title)

        if get_ipython():
            return f
        else:
            f.view(cleanup=True)
            return None

    def summarize(self, style: str = "gfm") -> Optional[Markdown]:
        """
        Prints a summary table of the apparatus.

        Arguments:
        - `style`: Either `gfm` for GitHub-flavored Markdown or `ascii`. If equal to `gfm` and in a Jupyter notebook, returns a rendered HTML version of the GFM table.

        Returns:
        - In Jupyter, a nice HTML table. Otherwise, the output is printed to the terminal.
        """

        if style == "ascii":
            tableStyle = AsciiTable
        else:
            tableStyle = GithubFlavoredMarkdownTable

        # create a components table
        summary = [["Name", "Type"]]  # header rows of components table
        for component in sorted(self.components, key=lambda x: x.__class__.__name__):
            summary.append([component.name, component.__class__.__name__])

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
        total_length = 0 * _ureg.mm
        total_volume = 0 * _ureg.ml
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
                "**Total**" if style == "gfm" else "Total",
                "n/a",
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

        if get_ipython():
            if style == "gfm":
                md = (
                    f"### {components_table.title}\n\n"
                    f"{components_table.table}\n\n"
                    f"### {tubing_table.title} \n\n"
                    f"{tubing_table.table}"
                )
                return Markdown(md)

        print("Components")
        print(components_table.table)
        print("\nTubing")
        print(tubing_table.table)
        return None

    def _validate(self) -> bool:
        """
        Checks that the apparatus is valid.

        ::: tip
        Calling this function yourself is likely unnecessary because the `Protocol` class calls it upon instantiation.
        :::

        Returns:
        - Whether the apparatus is valid.
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
            if isinstance(valve.mapping, Mapping):
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

        Returns:
        - A description of apparatus. When in Jupyter, this string is wrapped in a `IPython.display.Markdown` object for nicer display.

        Raises:
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
        if get_ipython():
            return Markdown(result)
        return result
