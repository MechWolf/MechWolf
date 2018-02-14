# Flow Chemistry

The purpose of this module is to allow light weight flow chemistry experiment design in Python. Features include extensive error checking, flexibility, and user extensibility. 

## API Reference

### Apparatus

#### __init__
`__init__(self, name=None)`

Initialization of an `Apparatus` object. 

##### Arguments
* **name**: The name of the apparatus. If not given, defaults to "Apparatus_[number]".

#### add
`add(self, from_component, to_component, tube)`

Adds a connection between components to the apparatus.

##### Arguments
* **from_component**: Component object.
* **to_component**: Component object.
* **tube**: Tube object describing the connection between the two components.

#### visualize
`visualize(self, label=True, node_attr={}, edge_attr={}, graph_attr={}, format="pdf", filename=None)`

Creates a graphical visualization of the apparatus. For full list of acceptable attributes, see [here](https://www.graphviz.org/doc/info/attrs.html) and [here](http://graphviz.readthedocs.io/en/stable/manual.html#attributes)

##### Arguments
* **label**: Boolean. If true, displays the name of the apparatus as the title for the graph. 
* **node_attr**: Dictionary. Attributes to modify the display of nodes.
* **edge_attr**: Dictionary. Attributes to modify the display of edges.
* **graph_attr**: Dictionary. Attributes to modify the display of the graph.
* **format**: String. The output format for rendering.
* **filename**: String. The filename of the output file. If `None`, defaults to the name of the apparatus.

#### summarize
`summarize(self)`

Prints a tabular summary of the apparatus.

#### validate
`validate(self)`

Ensures that the apparatus is valid. While you can call it yourself, creating a protocol automatically checks that the apparatus is valid.



### Protocol


#### __init__
`__init__(self, apparatus, duration=None, name=None)`

Initialize the `Protocol` object.

##### Arguments
* **apparatus**: Apparatus object that the protocol is for.
* **duration**: String. The duration of the protocol. If not given, all `stop_time`s must be given when adding procedures to the protocol. If set to `auto`, duration is inferred from the last time given by `add`.
* **name**: String. Name of the protocol.

#### add
`add(self, component, start_time="0 seconds", stop_time=None, duration=None, **kwargs)`

Add a procedure to the protocol. 

##### Arguments
* **component**: Component. The component which the procedure being added to the protocol if for.
* **start_time**: String or timedelta. The start time of the procedure relative to time 0 (the start time of the experiment).
* **stop_time**: String or timedelta. The stop time of the procedure relative to time 0 (the start time of the experiment).
* **duration**: String or timedelta. The duration of the procedure.
* **\*\*kwargs**: The parameters of the component that are being modified.

**Note:** If `start_time` is not given, it will be assumed to be the beginning of the protocol. Similarly, if `stop_time` is not given, it will be assumed to be the end of the protocol or the next time a procedure is added, whichever is first. Note that only one of `stop_time` and `duration` can be given.


#### compile
`compile(self, warnings=True)`

Ensures that the protocol is valid. While you can call it yourself, this is done automatically before any protocol is executed.

##### Arguments
* **warnings**: Boolean. Set to False to suppress warnings.


#### json
`json(self, warnings=True)`

Returns a JSON-formatted string of the compiled protocol.

##### Arguments
* **warnings**: Boolean. Set to False to suppress warnings.

