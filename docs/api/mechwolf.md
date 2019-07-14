---
sidebarDepth: 2
editLink: false
---
# MechWolf
## Apparatus

A unique network of components.

::: tip Note
The same components may be organized into multiple distinct apparatuses, depending on the connections between them.
:::

Attributes:
- `network`: A list of tuples in the form `(from_component, to_component, tube)` describing the configuration of the apparatus.
- `components` (set): The components that make up the apparatus.

See also the arguments of `__init__()` for more attributes.
### __init__

```python
__init__(self, name: Optional[str] = None, description: Optional[str] = None)
```

#### Arguments
- `name`: The name of the apparatus. Defaults to "Apparatus_X" where *X* is apparatus count. This should be short and sweet.
- `description`: A description of the apparatus. Can be as long and wordy as you want.

### add

```python
add(
    self,
    from_component: Union[Component, Iterable],
    to_component: Component,
    tube: Tube,
) -> None
```

Adds connections to the apparatus.

#### Arguments
- `from_component`: The `Component` from which the flow is originating. If an iterable, all items in the iterable will be connected to the same component.
- `to_component`: The `Component` where the flow is going.
- `tube`: `Tube` that connects the components.

#### Raises
- `ValueError`: When the connection being added is invalid.

### visualize

```python
visualize(
    self,
    title: bool = True,
    label_tubes: bool = False,
    describe_vessels: bool = False,
    node_attr: dict = {},
    edge_attr: dict = {},
    graph_attr: dict = dict(splines="ortho"),
    file_format: str = "pdf",
    filename: Optional[str] = None,
) -> Optional[Digraph]
```

Generates a visualization of the graph of an apparatus.

For full list of acceptable Graphviz attributes for see [the graphviz.org docs](http://www.graphviz.org/doc/info/attrs.html) and [its Python API's docs](http://graphviz.readthedocs.io/en/stable/manual.html####attributes).

#### Arguments
- `title`: Whether to show the title in the output. Defaults to True.
- `label_tubes`: Whether to label the tubes between components with the length, inner diameter, and outer diameter.
- `describe_vessels`: Whether to display the names or content descriptions of `Vessel` components.
- `node_attr`: Controls the appearance of the nodes of the graph. Must be of the form `{"attribute": "value"}`.
- `edge_attr`: Controls the appearance of the edges of the graph. Must be of the form `{"attribute": "value"}`.
- `graph_attr`: Controls the appearance of the graph. Must be of the form `{"attribute": "value"}`. Defaults to orthogonal splines and a node separation of 1
- `file_format`: The output format of the graph, either "pdf" or "png".
- `filename`: The name of the output file. Defaults to the name of the apparatus.

#### Raises
- `ImportError`: When the visualization package is not installed.

### summarize

```python
summarize(self, style: str = "gfm") -> Optional[HTML]
```

Prints a summary table of the apparatus.

#### Arguments
- `style`: Either `gfm` for GitHub-flavored Markdown or `ascii`. If equal to `gfm` and in a Jupyter notebook, returns a rendered HTML version of the GFM table.

#### Returns
In Jupyter, a nice HTML table. Otherwise, the output is printed to the terminal.

### validate

```python
validate(self) -> bool
```

Checks that the apparatus is valid.

::: tip
Calling this function yourself is likely unnecessary because the `Protocol` class calls it upon instantiation.
:::

#### Returns
Whether the apparatus is valid.

### describe

```python
describe(self) -> Union[str, Markdown]
```

Generates a human-readable description of the apparatus.

#### Returns
- `str`: A description of apparatus. When in Jupyter, this string is wrapped in a `IPython.display.Markdown` object for nicer display.

#### Raises
- `RuntimeError`: When a component cannot be described.

## Protocol

A set of procedures for an apparatus.

A protocol is defined as a list of procedures, atomic steps for the individual active components of an apparatus.

::: tip
The same `Apparatus` object can create multiple distinct `Protocol` objects.
:::

Attributes:
- `apparatus`: The apparatus for which the protocol is being defined.
- `name`: The name of the protocol. Defaults to "Protocol_X" where *X* is protocol count.
### add

```python
add(
    self,
    component: Union[ActiveComponent, Iterable],
    start="0 seconds",
    stop=None,
    duration=None,
    **kwargs,
)
```

Adds a procedure to the protocol.

::: warning
If stop and duration are both `None`, the procedure's stop time will be inferred as the end of the protocol.
:::

#### Arguments
- `component_added`: The component(s) for which the procedure being added. If an interable, all components will have the same parameters.
- `start`: The start time of the procedure relative to the start of the protocol, such as `"5 seconds"`. May also be a `datetime.timedelta`. Defaults to `"0 seconds"`, *i.e.* the beginning of the protocol.
- `stop`: The stop time of the procedure relative to the start of the protocol, such as `"30 seconds"`. May also be a `datetime.timedelta`. May not be given if `duration` is used.
duration: The duration of the procedure, such as "1 hour". May not be used if `stop` is used.
- `**kwargs`: The state of the component for the procedure.

#### Raises
- `TypeError`: A component is not of the correct type (*i.e.* a Component object)
- `ValueError`: An error occurred when attempting to parse the kwargs.
- `RuntimeError`: Stop time of procedure is unable to be determined or invalid component.

### compile

```python
compile(self, dry_run: bool = True, _visualization: bool = False) -> dict
```

Compile the protocol into a dict of devices and their procedures.

#### Returns
A dict with components as the values and lists of their procedures as the value. The elements of the list of procedures are dicts with two keys: "time" in seconds, and "params", whose value is a dict of parameters for the procedure.

#### Raises
- `RuntimeError`: When compilation fails.

### yaml

```python
yaml(self) -> Union[str, Code]
```

Outputs the uncompiled procedures to YAML.

Internally, this is a conversion of the output of `Protocol.json` for the purpose of enhanced human readability.

#### Returns:
YAML of the procedure list. When in Jupyter, this string is wrapped in an `IPython.display.Code` object for nice syntax highlighting.

### json

```python
json(self) -> Union[str, Code]
```

Outputs the uncompiled procedures to JSON.

#### Returns
JSON of the protocol. When in Jupyter, this string is wrapped in a `IPython.display.Code` object for nice syntax highlighting.

### visualize

```python
visualize(self, browser: bool = True) -> Union[str, HTML]
```

Generates a Gantt plot visualization of the protocol.

#### Arguments
- `browser`: Whether to open in the browser.

#### Returns
The html of the visualization. When in Jupyter, this string is wrapped in a `IPython.display.HTML` object for interactive display.

### execute

```python
execute(self, dry_run: bool = False, verbosity: str = "info") -> Experiment
```

Executes the procedure.

#### Arguments
- `dry_run`: Whether to simulate the experiment or actually perform it. Defaults to `False`, which means executing the protocol on real hardware.
- `verbosity`: The level of logging verbosity. One of "critical", "error", "warning", "success", "info", "debug", or "trace" in descending order of severity. "debug" and (especially) "trace" are not meant to be used regularly, as they generate significant amounts of usually useless information. However, these verbosity levels are useful for tracing where exactly a bug was generated, especially if no error message was thrown.

#### Returns
An `Experiment` object. In a Jupyter notebook, the object yields an interactive visualization.

#### Raises
`RuntimeError`: When attempting to execute a protocol on invalid components.

### clear_procedures

```python
clear_procedures(self) -> None
```

Reset the protocol's procedures.

## Experiment

Experiments contain all data from execution of a protocol.
### __init__

```python
__init__(self, protocol: "Protocol", compiled_protocol: dict, verbosity: str)
```

#### Arguments
- `protocol`: The protocol for which the experiment was conducted
- `compiled_protocol`: The results of `protocol.compile()`.
- `verbosity`: See `Protocol.execute` for a description of the verbosity options.


