# Documentation Guidelines

MechWolf prides itself on clear, thorough documentation.
We follow [established guidelines](doi.org/10.1371/journal.pcbi.1006561) for documentation of scientific software.
As a rule, all new code must be documented in order to be merged.
Specifically, this means:

1. [Docstrings on all classes and functions](#docstrings)
1. [Comments in the code](#comments)
1. [Type annotations for function signatures](#type-annotations)
1. [Release notes](#release-notes)

Let's break it down.

## Docstrings

All MechWolf classes and functions need docstrings.
These docstrings are used as the basis of the [automatically generated documentation](/api/overview) on this very site.
MechWolf docstrings must be of a specific format in order to be properly parsed a webpage.
Specifically, they must be written in valid [GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/).

The best way to describe a MechWolf docstring is by example:

````md
A single sentence describing the class or function.

Note that the sentence ends in a period.
Below the short introduction, there may be one or more paragraphs of details.
This paragraph should written with one sentence per line.
The reason for this is that it results in smaller git diffs.
After (or before) the paragraph, you can also optionally include a tip or warning.

::: warning Optional Title
This isn't a real docstring.
:::

You can even include an example!

```python
>>> print("hello world!")
hello world!
```

Then, you should include arguments (for a function) or attributes (for a class).

Args:

- `arg1`: The first argument.
- `arg2`: The second argument.

Returns:

A description of the return value, if a function.

Raises:

- `RuntimeError`: A list of the errors that can be raised by the function, if applicable.
````

## Comments

Comments are a key source of documentation in MechWolf since they describe what's actually going on in the code.
We expect all code to be thoroughly commented such that a competent third party can understand what is going on just from the comments.
During code review, we can always remove unneeded comments, so don't worry about having too many.
In fact, to quote [_Ten Simple Rules for Documenting Scientific Software_](https://doi.org/10.1371/journal.pcbi.1006561):

> **When in doubt, err on the side of more comments.**

To learn more about Python commenting, take a look at [this guide](https://realpython.com/python-comments-guide/), or follow the example of the current [MechWolf repository](https://github.com/Benjamin-Lee/mechwolf).

## Type annotations

Type annotation, introduced in [PEP 484](https://www.python.org/dev/peps/pep-0484), is one of the major new features of Python 3.
We are currently in the process of annotating all code in MechWolf.
There are two primary reasons for this: first, it allows for better typehinting, which in turn makes developing the library require less cognitive burden.
Many modern text editors and IDEs are able to take advantage of type hints to provide a better, faster development experience.
Second (and more importantly), it allows for static code analysis to find bugs using tools such as [Mypy](https://github.com/python/mypy) and [Pyre](https://pyre-check.org).
All new code, as well as changes to the existing code base require full type annotation.
Eventually, we aim to achieve 100% type annotation coverage, at which point we will add type checking to our continuous integration system.

One particularly useful resource is the [Mypy Python 3 cheat sheet](https://mypy.readthedocs.io/en/latest/cheat_sheet_py3.html), which goes over type annotation by example.

## Release notes

All changes to the MechWolf source code after release 0.1 require release notes.
More information to come.
