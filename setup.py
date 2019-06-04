from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "readme.md")) as f:
    long_description = f.read()

setup(
    name="mechwolf",
    version="0.0.2",
    description="Continuous flow process description, analysis, and automation",
    long_description=long_description,
    url="https://github.com/benjamin-lee/MechWolf",
    author="Benjamin Lee and Alex Mijalis",
    author_email="benjamindlee@me.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.7",
    packages=find_packages(),
    tests_require=["pytest"],
    setup_requires=["pytest-runner"],
    install_requires=[
        "CIRpy",
        "Jinja2",
        "mistune",
        "terminaltables",
        "blessings",
        "networkx",
        "Click",
        "bokeh",
        "click_didyoumean",
        "Pint",
        "graphviz",
        "ipython>=7.0",
        "pyserial",
        "PyYAML",
        "jupyter",
        "stackprinter",
    ],
    extras_require={
        "dev": [
            "pre-commit",
            "isort",
            "pytest",
            "flake8",
            "pipdeptree",
            "pipreqs",
            "black",
        ]
    },
    entry_points={
        "console_scripts": ["mechwolf=mechwolf.cli:cli", "mw=mechwolf.cli:cli"]
    },
)
