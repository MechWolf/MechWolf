# Installation

## From Conda (recommended)

The easiest way to get MechWolf and all its dependencies is to use [Conda](https://conda.io/en/latest/), an open source package manager.
There are several ways to get MechWolf from Conda.

### Visual installation

::: tip
If you run into any issues during installation, please contact us [here](https://github.com/MechWolf/MechWolf/issues/new?assignees=Benjamin-Lee&template=installation_help.md&title=).
:::

If you're new to programming, you can get MechWolf up and running _without_ having to use the command line.
To do so, follow these steps:

1. Install [Anaconda Distribution](https://www.anaconda.com/distribution/) **for Python 3.7**.
   Anaconda is an open source set of tools for scientific Python and it includes the Conda package manager that we'll be using to install MechWolf (confusing, we know).
2. Open the Anaconda Navigator application, a graphical interface to Conda. This should have been installed on your computer by Anaconda.
   Click "environments" on the left side (circled in red).
   ![envs](/anaconda_envs.png)
3. On the bottom click "create" (circled in red) to create a new environment in which MechWolf will live.
   ![create_env_1](/anaconda_create_env_1.png)
4. Then, enter the details of the environment. You can call it whatever you want, but **be sure to select Python 3.7 or above**.
   ![create_env_2](/anaconda_create_env_2.png)
5. Click the "channels" button.
   ![add_channel_1](/anaconda_add_channel_1.png)
6. Click "add", type `conda-forge`, hit enter and click "update channels".
   ![add_channel_2](/anaconda_add_channel_2.png)
7. Next, click the dropdown (circled in red) and select "all". Then, type `mechwolf` in the search box (circled in magenta), click the checkbox next to MechWolf (circled in green).
   Then click "apply" (circled in blue).
   It may take a moment for MechWolf to show up in the search results.
   ![install_mw](/anaconda_install_mw.png)
8. Go back to the homepage by clicking "home" (circled in red) and then launch a Jupyter notebook (circled on green).
   ![launch_nb](/anaconda_launch_nb.png)

### Command line

With [Conda](https://conda.io/en/latest/) installed (possibly via [Miniconda](https://docs.conda.io/en/latest/miniconda.html)), run:

```
conda install -c conda-forge mechwolf
```

## From PyPI

::: tip Note
This may take a long time on a Raspberry Pi.
:::

MechWolf is available from [PyPI](https://pypi.org), the Python Package Index.
Installation is a breeze.
In your [virtualenv](/guide/gentle_intro#create-a-virtualenv-optional), use the `pip` command to install MechWolf:

```
$ pip install mechwolf
```

In addition, to use apparatus visualization, you'll need to get [Graphviz](https://graphviz.gitlab.io) yourself.
See the installation instructions [here](https://graphviz.gitlab.io/download/).

## From source

If you would like to use the development version of MechWolf, which is **not guaranteed to be safe or stable**, you can install MechWolf directly from the GitHub repository using the following command:

```
$ pip install git+https://github.com/MechWolf/MechWolf.git
```
