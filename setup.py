from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'readme.md')) as f:
    long_description = f.read()

setup(
    name='mechwolf',
    version='0.0.1',
    description='Continuous flow process description, analysis, and automation',
    long_description=long_description,
    url='https://github.com/benjamin-lee/MechWolf',
    author='Benjamin Lee and Alex Mijalis',
    author_email='benjamindlee@me.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering :: Chemistry",
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
    packages=find_packages(),
    tests_require=["pytest"],
    setup_requires=['pytest-runner'],
    install_requires=[
        "terminaltables",
        "pint",
        "networkx",
        "CIRpy",
        "colorama",
        "pyyaml",
        "requests",
        "xkcdpass",
        "pick",
        "click",
        "rsa",
        "yamlordereddictloader",
        "keyring",
        "urllib3",
        "itsdangerous"],
    extras_require={
        'vis': ['plotly', "graphviz"],
        'client': ["pyserial", "aiohttp"],
        'hub': ["schedule", "flask", "pyopenssl", "gevent"]
    },
    entry_points={'console_scripts': ['mechwolf=cli:cli']},
)
