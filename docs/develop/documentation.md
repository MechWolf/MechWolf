# Documentation Guidelines

MechWolf prides itself on clear, thorough documentation.
We follow [established guidelines](https://doi.org/10.1371/journal.pcbi.1006561) for documentation of scientific software.
As a rule, all new code must be documented in order to be merged.
Specifically, this means:

1. [Docstrings on all classes and functions](#docstrings)
1. [Comments in the code](#comments)
1. [Type annotations for function signatures](#type-annotations)
1. [Release notes](#release-notes)

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
All sentences should end in a period.
After (or before) the paragraph, you can also optionally include a tip or warning.

::: warning Optional Title
This isn't a real docstring.
:::

You can even include an example!

```python
>>> print("hello world!")
hello world!
```

Then, you should include arguments (for a function) and/or attributes (for a class).

Arguments:

- `arg1`: The first argument.
- `arg2`: The second argument.

Returns:

- A description of the return value, if a function.
  This should be a list, even if its the only element.
  Note that each sentence should also be on a separate line aligned with the first letter of the first line.

Raises:

- `RuntimeError`: A list of the errors that can be raised by the function, if applicable.
  Also a list.
````

Classes may also have an optional field entitled "Attributes" in their class docstring (not the `__init__()` docstring).

To quote [PEP8](https://www.python.org/dev/peps/pep-0008/#a-foolish-consistency-is-the-hobgoblin-of-little-minds):

> **Consistency within a project is more important. Consistency within one module or function is the most important.**

When in doubt, please check the existing source code for examples, especially in the file being modified.

## Comments

Comments are a key source of documentation in MechWolf since they describe what's actually going on in the code.
We expect all code to be thoroughly commented such that a competent third party can understand what is going on just from the comments.
During code review, we can always remove unneeded comments, so don't worry about having too many.
In fact, to quote [_Ten Simple Rules for Documenting Scientific Software_](https://doi.org/10.1371/journal.pcbi.1006561):

> **When in doubt, err on the side of more comments.**

To learn more about Python commenting, take a look at [this guide](https://realpython.com/python-comments-guide/), or follow the example of the current [MechWolf repository](https://github.com/Benjamin-Lee/mechwolf).

## Type annotations

Type annotation, introduced in [PEP 484](https://www.python.org/dev/peps/pep-0484), is one of the major new features of Python 3.
In essence, type annotation allows bugs like this to be caught _before_ runtime:

```python
def foo(x, y):
    return x + y

foo(1, "two") # this will raise an uncaught error!
```

As you know, you can't add a string to an integer in Python, but the only way to find that out is to attempt to run the code.
Because we don't want to be encountering errors in live code running hardware, we annotate what types of Python objects our functions require so that errors can automatically be detected:

```python
def foo(x: int, y: int) -> int:
    return x + y

foo(1, "two") # Mypy will catch this bug!
```

All code in MechWolf is fully type annotated in this manner.
Another benefit comes of using type annotations: it allows for better typehinting, which in turn makes developing the library require less cognitive burden.
Many modern text editors and IDEs are able to take advantage of type hints to provide a better, faster development experience.
For example, VSCode shows the type of variables when they are hovered over by looking back at its type annotation.

We rely on Python's official type checker, [Mypy](https://github.com/python/mypy) to validate MechWolf's source code.
To run Mypy yourself, be sure to use the command `mypy mechwolf/ --ignore-missing-import` from the main directory (not the MechWolf folder).
We currently ignore missing imports due to some modules we use not having declared type annotations.
As type checking becomes common in the Python ecosystem, we hope to enable full type checking of imported modules.

## Release notes

All changes to the MechWolf source code after release 0.1 require release notes.
More information to come.
