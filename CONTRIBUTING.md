# Contributing

Thanks for contributing to MechWolf!
We appreciate all the help we can get and every little bit counts.
You don't need to be a technical expert to help out, and credit will always be given.

There are a bunch of ways that you can contribute to the project:

## How to contribute

### Bug reports

The easiest way to help out is to let us know if something is wrong so we can fix it.
To file a bug report, go to please click [here](https://github.com/Benjamin-Lee/MechWolf/issues/new?assignees=&labels=bug&template=bug_report.md&title=) and fill out the form with as much information as you can.

### Feature requests

If you have an idea of way to make MechWolf better (even if you're not sure how to implement it), we want to know!
In order to help us keep track of feature requests, we ask that you open a [GitHub issue](https://github.com/Benjamin-Lee/MechWolf/issues/new?assignees=&labels=&template=feature_request.md&title=) using the feature request form.

### Write documentation

We can always use more and clearer documentation.
Our docs are written in a combination of [Markdown](https://commonmark.org/help/) (for normal text such as this), [reStructuredText](http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) (for technical docs, such as for the API), and [Jupyter notebooks](https://jupyter-notebook.readthedocs.io/en/stable/) (for the interactive tutorials).

### Fix bugs and implement features

Look through the [GitHub issues](https://github.com/Benjamin-Lee/MechWolf/issues/) for unfixed bugs and unimplemented features.
Anything tagged with "enhancement" and "help wanted" is open to whoever wants to do it.

## Get started

1. First, [fork the repository on GitHub](https://github.com/Benjamin-Lee/MechWolf).
1. Clone your fork:
    ```
    $ git clone git@github.com:your_name_here/MechWolf.git
    ```
1. Set up your virtualenv:
    ```
    $ virtualenv -p python3.7 mechwolf-dev-env
    $ source mechwolf-dev-env/bin/activate
    ```
1. Install MechWolf with the developer dependencies:
    ```
    (mechwolf-dev-env) $ cd MechWolf
    (mechwolf-dev-env) $ pip install -e .[dev]
    ```
1. Set up [pre-commit](https://pre-commit.com/):
    ```
    (mechwolf-dev-env) $ pre-commit install
    ```
1. Make a new branch:
    ```
    (mechwolf-dev-env) $ git checkout -b name-of-your-bugfix-or-feature
    ```
1. Once you're done making your changes, make sure that the test suite passes:
    ```
    (mechwolf-dev-env) $ pytest
    ```
1. Then, make your commit:
    ```
    (mechwolf-dev-env) $ git add *
    (mechwolf-dev-env) $ git commit -am "commit message here"
    (mechwolf-dev-env) $ git push origin name-of-your-bugfix-or-feature
    ```
    Pre-commit will make sure that your changes conform to our coding style, as well as that it passes some [static analysis tests](http://flake8.pycqa.org/en/latest/).
1. When you're done, create a pull request for us to review.
    As a general rule, pull requests should ensure that the tests and documentation are updated.
    Furthermore, it should be compatible with all supported Python versions, which is currently Python 3.7 and 3.8.
