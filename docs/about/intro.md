# Welcome to MechWolf

MechWolf is a Python framework for automating continuous flow processes.
It was developed as a collaboration between computer scientists, chemists, and complete novices to be used by anyone wanting to do better, faster, more reproducible flow-based science.
Features include:

- Natural language description, analysis, and visualization of continuous flow networks
- Automated execution of protocols
- Full user extensibility
- Smart default settings, designed by scientists for scientists
- Extensive checking to prevent potentially costly and dangerous errors _before_ runtime
- Natural language parsing of times and quantities
- Thorough documentation and tutorials

### What does "MechWolf" even mean?

Simply, "MechWolf" is an anagram of "flow chem". This tool can do so much more
than just chemistry automation, so we decided not to pigeonhole ourselves by
calling the project "flow chem". We like to think MechWolf is a **way** cooler
name anyway.

### Three Minutes to MechWolf

Let's say you're trying to automate the production of [acetaminophen](https://en.wikipedia.org/wiki/Paracetamol), a popular pain reliever and fever
reducer. The reaction involves combining two chemicals, 4-aminophenol and acetic
anhydride. The basic level of organization in MechWolf are individual
components, such as the vessels and pumps. Let's go ahead and create them:

```python
import mechwolf as mw

# define the vessels
aminophenol = mw.Vessel("15 mL 4-aminophenol")
acetic_anhydride = mw.Vessel("15 mL acetic anhydride")
acetaminophen = mw.Vessel("acetaminophen")

# define the pumps
pump_1 = mw.Pump()
pump_2 = mw.Pump()

# define the mixer
mixer = mw.TMixer()
```

That wasn’t too bad! Just as putting vessels and pumps on a lab bench doesn’t actually do anything, we’re going to need to tell MechWolf what the configuration of the components is.

We can do this by creating an `Apparatus` object. To add connections between components, we need to tell MechWolf three things: where the connection is from, where it’s going, and how they are actually connected. Tubing type can have a significant effect on reproducibility, so we require that you explicitly specify what tubing you are using when connecting components. This sounds complicated, but it is actually easy in practice:

```python
# same tube specs for all tubes
tube = mw.Tube(length="1 m", ID="1/16 in", OD="2/16 in", material="PVC")

# create the Apparatus object
A = mw.Apparatus()

# add the connections
A.add(aminophenol, pump_1, tube)  # connect aminophenol vessel to pump_1
A.add(acetic_anhydride, pump_2, tube)  # connect acetic_anhydride vessel to pump_2
A.add([pump_1, pump_2], mixer, tube)  # connect pump_1 and pump_2 to mixer
A.add(mixer, acetaminophen, tube)  # connect mixer to the output vessel
```

With the Apparatus object, we can do so much. If we call `summarize()`, we’ll get a clean tabular describe of our apparatus like this with summary values automatically computed:

```python
A.summarize()
```

<h3>Components</h3><table>
<thead><tr>
<th>Name</th>
<th>Type</th>
</tr>
</thead>
<tbody>
<tr>
<td>acetaminophen (N-(4-Hydroxyphenyl)acetamide)</td>
<td>Vessel</td>
</tr>
<tr>
<td>15 mL 4-aminophenol</td>
<td>Vessel</td>
</tr>
<tr>
<td>15 mL acetic anhydride (Acetyl acetate)</td>
<td>Vessel</td>
</tr>
<tr>
<td>pump_2</td>
<td>Pump</td>
</tr>
<tr>
<td>TMixer_0</td>
<td>TMixer</td>
</tr>
<tr>
<td>pump_1</td>
<td>Pump</td>
</tr>
</tbody>
</table>
<h3>Tubing</h3><table>
<thead><tr>
<th>From</th>
<th>To</th>
<th>Length</th>
<th>Inner Diameter</th>
<th>Outer Diameter</th>
<th>Volume</th>
<th>Material</th>
</tr>
</thead>
<tbody>
<tr>
<td>aminophenol</td>
<td>pump_1</td>
<td>1 meter</td>
<td>0.0625 inch</td>
<td>0.125 inch</td>
<td>1.9793 milliliter</td>
<td>PVC</td>
</tr>
<tr>
<td>acetic anhydride</td>
<td>pump_2</td>
<td>1 meter</td>
<td>0.0625 inch</td>
<td>0.125 inch</td>
<td>1.9793 milliliter</td>
<td>PVC</td>
</tr>
<tr>
<td>pump_1</td>
<td>TMixer_0</td>
<td>1 meter</td>
<td>0.0625 inch</td>
<td>0.125 inch</td>
<td>1.9793 milliliter</td>
<td>PVC</td>
</tr>
<tr>
<td>pump_2</td>
<td>TMixer_0</td>
<td>1 meter</td>
<td>0.0625 inch</td>
<td>0.125 inch</td>
<td>1.9793 milliliter</td>
<td>PVC</td>
</tr>
<tr>
<td>TMixer_0</td>
<td>acetaminophen</td>
<td>1 meter</td>
<td>0.0625 inch</td>
<td>0.125 inch</td>
<td>1.9793 milliliter</td>
<td>PVC</td>
</tr>
<tr>
<td></td>
<td><strong>Total</strong></td>
<td>5000.0 millimeter</td>
<td>n/a</td>
<td>n/a</td>
<td>9.8966 milliliter</td>
<td>n/a</td>
</tr>
</tbody>
</table>

But wait, there’s more! `visualize()` will create a diagram of the network:

```python
A.visualize()
```

![svg](index_files/index_9_0.svg)

It’s fully customizable, so you can decide whether to show the details of the tubing, the name of the apparatus, and more. And that’s not all either. `describe()` will generate an SI-ready description of the apparatus:

```python
A.describe()
```

A vessel containing 15 mL 4-aminophenol was connected to Pump pump_1 using PVC tubing (length 1 meter, ID 0.0625 inch, OD 0.125 inch). A vessel containing 15 mL acetic anhydride (Acetyl acetate) was connected to Pump pump_2 using PVC tubing (length 1 meter, ID 0.0625 inch, OD 0.125 inch). Pump pump_1 was connected to TMixer TMixer_0 using PVC tubing (length 1 meter, ID 0.0625 inch, OD 0.125 inch). Pump pump_2 was connected to TMixer TMixer_0 using PVC tubing (length 1 meter, ID 0.0625 inch, OD 0.125 inch). TMixer TMixer_0 was connected to a vessel containing acetaminophen (N-(4-Hydroxyphenyl)acetamide) using PVC tubing (length 1 meter, ID 0.0625 inch, OD 0.125 inch).

Now that we’ve gone over how to define an apparatus and all the different ways to inspect it, let’s make it synthesize acetaminophen. We do that with a `Protocol`, a list of procedures defined for an `Apparatus`. For this reaction, it’s as simple as deciding the flow rate and duration for which to run the pumps:

```python
# create the Protocol object
P = mw.Protocol(A, name="acetaminophen synthesis")
P.add([pump_1, pump_2], duration="15 seconds", rate="1 mL/min")
```

It’s really that simple to create protocols. We can visualize it equally simply with `visualize()`:

```python
P.visualize()
```

<div id="timeline"></div>
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
<script charset="utf-8">
	google.charts.load('current', {'packages':['timeline']});
	google.charts.setOnLoadCallback(drawChart);
	function drawChart() {
		var container = document.getElementById('timeline');
		var chart = new google.visualization.Timeline(container);
		var dataTable = new google.visualization.DataTable();
		var options = { timeline: {
                barLabelStyle: {opacity: 0}},
			avoidOverlappingGridLines: false
		 };

    	dataTable.addColumn({ type: 'string', id: 'Component' });
    	dataTable.addColumn({ type: 'string', id: 'Setting' });
    	dataTable.addColumn({ type: 'date', id: 'Start' });
    	dataTable.addColumn({ type: 'date', id: 'End' });
    	dataTable.addRows([

    		[ "pump_1", "{'rate': '1 mL/min'}", new Date(0, 0, 0, 0, 0, 0), new Date(0, 0, 0, 0, 0, 15) ],

    		[ "pump_2", "{'rate': '1 mL/min'}", new Date(0, 0, 0, 0, 0, 0), new Date(0, 0, 0, 0, 0, 15) ],

    		]);
    	chart.draw(dataTable, options);
    }

</script>

Since we have a good idea of what our protocol is going to do, let’s go ahead and compile it. This will convert the procedure we added to the protocol into a list of instructions that can be passed to the components. We can compile it directly with `compile()` but let’s get it in YAML format for the sake of readability by calling `yaml()`:

```python
P.yaml()
```

Just as we expect, the pumps will both turn on to 1 mL/min at time 0 and turn off 900 seconds (15 minutes) later. When we’re ready to actually execute the protocol, we just call `execute()` and MechWolf will do the rest, ensuring that both pumps have their protocols and start in sync.

```python
P.execute(dry_run=True)
```
