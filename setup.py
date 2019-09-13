from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md")) as f:
    long_description = f.read()

setup(
    name="mechwolf",
    version="0.1.1.dev0",
    description="Continuous flow process description, analysis, and automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MechWolf/MechWolf",
    author="Benjamin Lee and Alex Mijalis",
    author_email="benjamindlee@me.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    python_requires=">=3.7",
    packages=find_packages(),
    tests_require=["pytest"],
    setup_requires=["pytest-runner"],
    install_requires=[
        "aiofiles",
        "aioserial",
        "altair",
        "bokeh",
        "graphviz",
        "ipython>=7.0",
        "ipywidgets",
        "jupyter",
        "loguru",
        "nest_asyncio",
        "networkx",
        "Pint",
        "PyYAML",
        "terminaltables",
        "vega",
        "xxhash",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "isort",
            "mypy",
            "pipdeptree",
            "pipreqs",
            "pre-commit",
            "pytest",
            "zest.releaser",
        ]
    },
)
