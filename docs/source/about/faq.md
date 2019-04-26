# FAQ

## What is MechWolf?

MechWolf is a Python package for continuous process automation. It
consists of two main parts: a Python library that allows you to describe
and analyze apparatuses and protocols as well as a system to execute the
protocols. It greatly increases the speed and reproducibility of
synthetic experimentation and lowers the cost and time barriers to
building custom automated synthesizers.

## Why automate synthesis?

Most specialty chemicals are still made by hand, one batch at a time,
using chemical processes not amenable to automation or to truly complete
documentation. Only a few types of molecules, notably DNA, are now made
by specialized automated synthesizers, a development that laid the
foundation for genome technologies.

## What can MechWolf enable?

MechWolf greatly increases the speed and reproducibility of synthetic
experimentation and lowers the cost and time barriers to building custom
automated synthesizers. These features make on-demand synthesis
accessible to a much wider audience worldwide. MechWolf can drive the
discovery of new chemical and biological processes as well as the
application of machine learning to synthetic processes.

## Do I need to know how to code?

Yes. However, we prepared [a guide for non-coders](../guide/gentle_intro) that will ease you into it.

## Why don't you support Python \<3.7?

[f strings](https://www.python.org/dev/peps/pep-0498/) are the best thing since sliced bread and [asynchronous generators](https://www.python.org/dev/peps/pep-0492/) are pretty neat too.
In all seriousness, execution depends on asynchronous code and Python 3.7 has the best support of all the Python versions.

## Is this only for \[insert field here\]?

No. MechWolf is field agnostic. If it flows, MechWolf is capable of handling it.

## How can I get help?

Take a look at our [support page](support).

## Can I use MechWolf for commercial purposes?

Yes. MechWolf is licensed under the permissive [GNU General Public License v3.0](license).

## Where can I get high-resolution versions of MechWolf's logo?

High-res versions are available in the [logos directory](https://github.com/Benjamin-Lee/MechWolf/tree/master/logo).

## How do I cite MechWolf?

To be determined when MechWolf is published!

## What makes MechWolf different from prior code?

Prior code specified individual components, such as for 3D printers, or was for running protocols on pre-built setups.
MechWolf is the first program to allow full specification of not only the components, but also the connections of those components into apparatuses.
MechWolf also allows the definition and execution of protocols for these apparatuses.
MechWolf has the additional addition of being self-documenting and designed from the start for user extensibility.

## How was MechWolf started?

A project team lead by Prof. Nicola Pohl (Indiana University) with Harvard undergraduates [Benjamin Lee](http://www.github.com/benjamin-lee) and Myles Ingram and MIT graduate student Alex Mijalis came together with support from the Radcliffe Institute for Advanced Study at Harvard University in 2017.
