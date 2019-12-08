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

Laboratory-scale chemical synthesis has largely been done by hand since the time of alchemy.
Experimental reproducibility is harmed by this paradigm both because individual experimenters may not perform the same experiment precisely the same way each time and because imprecision in the communication of the experimental protocol between researchers may result in different results.
However, automating and scaling these types of experiments is a challenge in part because it is still not a trivial task to design, assemble, and reliably control a set of computerized laboratory equipment to execute specific task.

Continuous-flow experimentation is an alternative approach to chemical synthesis in which reactions occur continuously as the reagents are pumped together.
Thus, every step of the reaction is occurring at the same time.
Continuous-flow systems have been used for the synthesis of biomolecules [@Mijalis2017], pharmaceuticals [@Kitson2018], and fragarences [@Morin2019].
This type of experiment lends itself more readily to automation than step-by-step batch synthesis, but the ability to simultaneously control and monitor the pumps, sensors, heaters, and other components is still an open problem.

MechWolf is a Python package that aims to solve this proven by integrating chemical process design, analysis, and execution for both continuous-flow and batch experiments [@acs2018].
Often run on low-cost, highly constrained systems, such Raspberry Pis, MechWolf also enables chemists around the world to automatically collect data as their experiment executes and remotely monitor the experiment's progress.
A key aspect of the automated execution feature is that, in the event of an error, the system shuts down immediately.
However, due to hardware limitations, failures often do not raise errors and false positives are frequent.
Due to the reactive nature of the chemicals involved, undetected failures also pose a safety concern.

Therefore, it is important that MechWolf be able to monitor sensor data in real time to identify uncommanded changes to the system's state indictable of a failure.
Furthermore, this system must be able to work on devices without an internet connection and with extremely limited memory availability.
Because all flow-based robotic chemistry systems depend on one or more pumps to move liquids and the high failure rate of the pumps used in these systems, we identified autonomous pump monitoring as key feature to enable safer experimentation.

# Related work

# Methods

Because the pumps use in chemical systems generate sine waves when monitored by UV/visible light spectroscopy sensors, we focused on identifying anomalies with the waveforms present in the sensor data.
Since the devices have limited compute and memory capacity, we decided to use a recently published tree-based method, the robust random cut forest (RRCF) for anomaly detection on the data streams [@rrcf].
RRCF enables us to precisely control the amount of memory used for anomaly detection to ensure that sufficient memory is available for MechWolf.
We eliminated threshold-based methods as too simple to capture the types of anomalies common to pumps in chemical systems.

We extended MechWolf by creating a virtual sensor capable of simulating various known failure modalities.
We then injected noise into the sensor's sine wave output.
To eliminate this noise, we used a moving average to smooth the data.
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
