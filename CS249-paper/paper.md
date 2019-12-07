---
title: Streaming Anomaly Detection for Constrained Robotic Chemistry Systems
author: Benjamin D. Lee and Soumil Singh
abstract: |
  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
bibliography: bibliography.bib
classoption: twocolumn
---

# Introduction

Chemistry research has largely been done via manual batch-wise processes since the time of alchemy.
Continuous-flow reactions are poised to change this paradigm, but the ability to robotically execute these experiments is hampered by difficulty in autonomously monitoring them.

MechWolf is a Python package that integrates chemical process design, analysis, and execution [@acs2018].
Often run on low-cost, highly constrained systems, such Raspberry Pis, MechWolf enables chemists around the world to automatically collect data as their experiment executes and remotely monitor the experiment's progress.
A key aspect of the automated execution feature is that, in the event of an error, the system shuts down immediately. However, due to hardware limitations, failures often do not raise errors and false positives are frequent.

Therefore, it is important that MechWolf be able to monitor sensor data in real time to identify uncommanded changes to the system's state.
Furthermore, this system must be able to work on devices without internet connections and with extremely limited memory availability.

Because all flow-based robotic chemistry systems depend on one or more pumps to move liquids and the high failure rate of the pumps used in these systems, we identified autonomous pump monitoring as key feature to enable safer experimentation.

# Related work

# Methods

Because the pumps use in chemical systems generate sine waves when monitored by UV/visible light spectroscopy sensors, we focused on identifying anomalies with the waveforms present in the sensor data.
Since the devices have limited compute and memory capacity, we decided to use a recently published tree-based method, the robust random cut forest (RRCF) for anomaly detection on the data streams [@rrcf].
RRCF enables us to precisely control the amount of memory used for anomaly detection to ensure that sufficient memory is available for MechWolf.
We eliminated threshold-based methods as too simple to capture the types of anomalies common to pumps in chemical systems.

We extended MechWolf by creating a virtual sensor capable of simulating various known failure modalities.
We then injected noise into the sensor's sine wave output.
To eliminate this noise, we used a moving average to smoothe the data.
We performed experiments in which we fed either the raw or smoothed sensor data into a Python implementation of RRCF [@Bartos2019] but found that both the performance and the false positive and false negative rates were unacceptable.
We therefore switched to using SciPy's signal processing routines for peak finding as a featurization method.
We tested these routines on both the raw and smoothed data.

For the real time monitoring capability, we intend to create a Flask local web server to run as a separate process on the device.
We have already modified the MechWolf `Sensor` object (which is responsible for reading data) to immediately post an asynchronous request to this server upon the receipt of new data.
The server will perform peak-finding and compute the anomaly score via RRCF.
If an anomaly is detected, it will return an error, which will be propagated by the `Sensor` object to the MechWolf protocol executor, which will in turn halt the experiment if configured to do so by the user.

The source code for our implementation of this feature is available online at <github.com/MechWolf/MechWolf/tree/CS249>.

# Results

# Conclusion

 <!-- leave this at the bottom because it writes the references at the end-->

# References
