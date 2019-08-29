# A _Very_ Gentle Introduction

## An Introduction to the Introduction

This gentle introduction is made for people with **absolutely no coding
experience** who are likely feeling very lost right now. To tell if this
guide is right for you, if you know what the command `pip install XXXXX`
does, then feel free to skip this section. If not, welcome! We'll cover
the background knowledge you'll need for the general [getting started guide](./getting_started).

## Learn the Very Basics of Python Syntax

MechWolf is written in Python, a high level programming language that is the _lingua franca_ of scientific computation.
This one language can do anything from [machine learning](http://keras.io) to [web server development](http://flask.pocoo.org) and now robotic chemistry. 
In order to get started with MechWolf, you'll need to learn the elements of Python syntax so that you'll have enough understanding to get tinkering.

[**Don't panic.**](https://en.wikipedia.org/wiki/Phrases_from_The_Hitchhiker%27s_Guide_to_the_Galaxy#Don't_Panic)

You don't need to know every nook and cranny of Python, just the most basic aspects of the language.
In fact, all of the Python that you'll need to get started is able to fit on [a two-page cheatsheet](https://perso.limsi.fr/pointal/_media/python:cours:mementopython3-english.pdf). 
(It might be a good idea to print it out and have it handy as you get started with Python.)
MechWolf's tutorials provide lots of examples to follow and use as the basis of your code, so you won't be starting from scratch. 

If you're looking for a quick guide to learn basic syntax with biologically inspired examples (rather than contrived computer science-y ones), take a look at the eight-page [Python for Biologists](https://pythonforbiologists.com/introduction) guide. 
You can pick up the basics of Python in a less than a day. 

Should you be interested in learning more about Python than just the very basics (and we certainly hope you are), here are a few good resources:

- [Codecademy](https://www.codecademy.com/learn/learn-python)
- [The official Python tutorial](https://docs.python.org/3/tutorial/index.html)
- [Learn Python the Hard Way](https://learnpythonthehardway.org/python3/) (note: despite the name, it isn't actually hard)

## Install Python 3.7 or greater

Although Python is likely already installed on your computer (especially
if you're using Mac or Linux), you probably don't have a recent enough
version of Python to support MechWolf. Python is available from the
[download page at Python.org](https://www.python.org/downloads/). For a
detailed guide, see [The Hitchhiker's Guide to Python section on
installing
Python 3](http://docs.python-guide.org/en/latest/starting/installation/).

::: warning Important
Be sure to download Python 3.7! MechWolf is written in Python 3.7, which is
not backwards compatible.
:::

## Learn the Command Line

In order to effectively use your computer to code, you'll want to
understand how to use the command line, at least to a cursory level. Go
over [common
commands](https://www.codecademy.com/articles/command-line-commands) to
at least get an idea of how to navigate the filesystem (`cd`, `ls`, and
`pwd`). This will be invaluable going forward.

## Create a virtualenv _(optional)_ <a id="virtualenv"></a>

[virtualenv](https://virtualenv.pypa.io/en/stable/) is a tool that
allows you to create isolated environments on your computer. For
example, imagine that one piece of code required having version 1.0 of
MechWolf but another required version 2.0. The solution is to run each
piece of code inside a virtual environment to keep their dependencies
separate. You don't have to do this step, but it's **highly
recommended** to prevent bad, unpredictable things from happening that
can be hard to debug. [The Hitchhiker's Guide to Python's section on
virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/#lower-level-virtualenv)
is well worth the read for getting a feel for virtualenv.

To install virtualenv use the following command in your terminal:

```bash
$ pip3 install virtualenv
```

Then in the directory you want to use, create a virtualenv named
mechwolf-env:

```bash
$ virtualenv -p python3.7 mechwolf-env
```

And then activate the environment with:

```bash
$ source mechwolf-env/bin/activate
```

You can leave the virtualenv at any time with the command:

```bash
(mechwolf-env) $ deactivate
```
