A *Very* Gentle Introduction
==============================

An Introduction to the Introduction
-----------------------------------

This gentle introduction is made for people with **absolutely no coding
experience** who are likely feeling very lost right now. To tell if this guide
is right for you, if you know what the command ``pip install XXXXX`` does, then
feel free to skip this section. If not, welcome! We'll cover the background
knowledge you'll need for the general :doc:`getting started guide
<../guide/getting_started>`.

Learn Python
------------

MechWolf is written in Python, a high level programming language that is the
*lingua franca* of scientific computation. This one language can do anything
from `machine learning <http://keras.io>`_ to `web server development
<http://flask.pocoo.org>`_ and now flow process automation. In order to get started
with MechWolf, you'll need to learn Python, specifically Python 3.

`Don't panic.
<https://en.wikipedia.org/wiki/Phrases_from_The_Hitchhiker%27s_Guide_to_the_Galaxy#Don't_Panic>`_

You can pick up the basics of Python in a day or two. A few good resources are listed here:

- `Codecademy <https://www.codecademy.com/learn/learn-python>`_
- `The official Python tutorial <https://docs.python.org/3/tutorial/index.html>`_
- `Learn Python the Hard Way <https://learnpythonthehardway.org/python3/>`_ (note: despite the name, it isn't actually hard)


Install Python 3.6 or greater
-----------------------------

Although Python is likely already installed on your computer (especially if
you're using Mac or Linux), you probably don't have a recent enough version of
Python to support MechWolf. Python is available from the `download page at
Python.org <https://www.python.org/downloads/>`_. For a detailed guide, see
`The Hitchhiker's Guide to Python section on installing Python 3
<http://docs.python-guide.org/en/latest/starting/installation/>`_.

.. Important::
   Be sure to download Python 3! MechWolf is written in Python 3, which is not
   backwards compatible.

Learn the Command Line
----------------------

In order to effectively use your computer to code, you'll want to understand how
to use the command line, at least to a cursory level. Go over `common commands
<https://www.codecademy.com/articles/command-line-commands>`_ to at least get an
idea of how to navigate the filesystem (``cd``, ``ls``, and ``pwd``). This will be
invaluable going forward.

.. _virtualenv_instructions:

Create a virtualenv *(optional)*
--------------------------------

`virtualenv <https://virtualenv.pypa.io/en/stable/>`_ is a tool that allows you
to create isolated environments on your computer. For example, imagine that one
piece of code required having version 1.0 of MechWolf but another required
version 2.0. The solution is to run each piece of code inside a virtual
environment to keep their dependencies separate. You don't have to do this step,
but it's **highly recommended** to prevent bad, unpredictable things from
happening that can be hard to debug. `The Hitchhiker's Guide to Python's section
on virtualenv
<http://docs.python-guide.org/en/latest/dev/virtualenvs/#lower-level-virtualenv>`_
is well worth the read for getting a feel for virtualenv.

To install virtualenv use the following command in your terminal::

    $ pip3 install virtualenv

Then in the directory you want to use, create a virtualenv named mechwolf-env::

    $ virtualenv -p python3.7 mechwolf-env

And then activate the environment with::

    $ source mechwolf-env/bin/activate

You can leave the virtualenv at any time with the command::

    (mechwolf-env) $ deactivate
