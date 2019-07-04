import networkx as nx
from graphviz import Digraph
from IPython.display import HTML, Markdown
from mistune import markdown
from terminaltables import AsciiTable, GithubFlavoredMarkdownTable

from . import ureg
from .components import Component, Tube, Valve, Vessel


class Apparatus(object):
    """A unique network of components.

    Note:
        The same components may be organized into multiple distinct apparatuses, depending on the connections between them.

    Attributes:
        network (list): A list of tuples in the form (from_component, to_component, tube) describing the configuration
            of the apparatus.
        components (set): The components that make up the apparatus.
        name (str): The name of the apparatus. Defaults to "Apparatus_X" where *X* is apparatus count.
    """

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
        """Adds a single connection to the apparatus.

        For args, see add().
        """
        if not issubclass(from_component.__class__, Component):
            raise ValueError("From component must be a subclass of Component")
        if not issubclass(to_component.__class__, Component):
            raise ValueError("To component must be a subclass of Component")
        if not issubclass(tube.__class__, Tube):
            raise ValueError("Tube must be an instance of Tube")

        self.network.append((from_component, to_component, tube))
        self.components.update([from_component, to_component])

    def add(self, from_component, to_component, tube):
        """Adds connections to the apparatus.

        Args:
            from_component (Component or Iterable): The :class:`~mechwolf.components.component.Component` from which the flow is originating. If an iterable, all items in the iterable will be connected to the same component.
            to_component (Component): The :class:`~mechwolf.components.component.Component` where the flow is going.
            tube (Tube): The :class:`~mechwolf.components.tube.Tube` that connects the components.

        Raises:
            ValueError: When the connection being added is invalid.
        """

        try:
            iter(from_component)
        except TypeError:
            from_component = [from_component]

        for component in from_component:
            self._add_single(component, to_component, tube)

    def visualize(
        self,
        title=True,
        label_tubes=False,
        describe_vessels=False,
        node_attr={},
        edge_attr={},
        graph_attr=dict(splines="ortho"),
        file_format="pdf",
        filename=None,
    ):
        """Generates a visualization of the graph of an apparatus.

        For full list of acceptable Graphviz attributes for see `the
        graphviz.org docs <http://www.graphviz.org/doc/info/attrs.html>`_ and
        `its Python API's docs
        <http://graphviz.readthedocs.io/en/stable/manual.html#attributes>`_.

        Args:
            title (bool, optional): Whether to show the title in the output. Defaults to True.
            label_tubes (bool, optional): Whether to label the tubes between components with the length, inner diameter,
                and outer diameter.
            describe_vessels (bool, optional): Whether to display the names or content descriptions of :class:`~mechwolf.components.vessel.Vessel` components.
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
        """
        self.validate()  # ensure apparatus is valid
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

        for x in self.network:
            tube_label = (
                f"Length {x[2].length}\nID {x[2].ID}\nOD {x[2].OD}"
                if label_tubes
                else ""
            )
            f.edge(
                x[0].description
                if isinstance(x[0], Vessel) and describe_vessels
                else x[0].name,
                x[1].description
                if isinstance(x[1], Vessel) and describe_vessels
                else x[1].name,
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

    def summarize(self, style="gfm"):
        """Prints a summary table of the apparatus.

        Args:
            style (str, optional): Either `gfm`` for GitHub-flavored Markdown or
                ``ascii``. If equal to ``gfm`` and in a Jupyter notebook, returns a
                rendered HTML version of the GFM table.

        Returns:
            IPython.display.HTML: In Jupyter, a nice HTML table. Otherwise, the
                output is printed to the terminal.
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

        # store and calculate the computed totals for tubing
        total_length = 0 * ureg.mm
        total_volume = 0 * ureg.ml
        for tube in [x[2] for x in self.network]:
            total_length += tube.length
            total_volume += tube.volume

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
        for edge in self.network:
            summary.append(
                [
                    edge[0].name,
                    edge[1].name,
                    round(edge[2].length, 4),
                    round(edge[2].ID, 4),
                    round(edge[2].OD, 4),
                    round(edge[2].volume.to("ml"), 4),
                    edge[2].material,
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

    def validate(self):
        """Ensures that the apparatus is valid.

        Note:
            Calling this function yourself is likely unnecessary because the
            :class:`Protocol` class calls it upon instantiation.

        Returns:
            bool: True if valid.

        Raises:
            RuntimeError: If the protocol is invalid.
        """
        G = nx.Graph()  # convert the network to an undirected NetworkX graph
        G.add_edges_from([(x[0], x[1]) for x in self.network])
        if not nx.is_connected(G):  # make sure that all of the components are connected
            raise RuntimeError("Unable to validate: not all components connected")

        # valve checking
        for valve in list(
            set([x[0] for x in self.network if issubclass(x[0].__class__, Valve)])
        ):
            for name in valve.mapping.keys():
                # ensure that valve's mapping components are part of apparatus
                if name not in [x.name for x in list(self.components)]:
                    raise RuntimeError(
                        f"Invalid mapping for Valve {valve}."
                        f" No component named {name} exists."
                    )
            # no more than one output from a valve (might have to change this)
            if len([x for x in self.network if x[0] == valve]) != 1:
                raise RuntimeError(f"Valve {valve} has multiple outputs.")

            # make sure valve's mapping is complete
            non_mapped_components = [
                x[0]
                for x in self.network
                if x[1] == valve and valve.mapping.get(x[0].name) is None
            ]
            if non_mapped_components:
                raise RuntimeError(
                    f"Valve {valve} has incomplete mapping."
                    f" No mapping for {non_mapped_components}"
                )

        return True

    def describe(self):
        """Generates a human-readable description of the apparatus.

        Returns:
            str: A description of apparatus. When in Jupyter, this string is
                wrapped in a :class:`IPython.display.Markdown` object for nicer
                display.

        Raises:
            RuntimeError: When a component cannot be described.
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
        for element in self.network:
            from_component, to_component, tube = (
                _description(element[0], capitalize=True),
                _description(element[1]),
                element[2],
            )
            result += (
                f"{from_component} was connected to"
                f" {to_component} using {element[2].material}"
                f" tubing (length {tube.length}, ID {element[2].ID}, OD {element[2].OD}). "
            )
        try:
            get_ipython
            return Markdown(result)
        except NameError:
            pass
        return result
