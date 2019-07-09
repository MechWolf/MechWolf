# Installation

## From PyPI (recommended)

::: tip NOTE

This will take a **long** time to compile on a Raspberry Pi.
:::

MechWolf is available from [PyPI](https://pypi.org), the Python Package
Index. Installation is a breeze. In your [virtualenv](/guide/gentle_intro#create-a-virtualenv-optional), use the `pip` command to install MechWolf:

```bash
    $ pip install mechwolf
```

## From source

If you would like to use the development version of MechWolf, which is
**not guaranteed to be safe or stable**, you can install MechWolf
directly from the GitHub repository using the following command:

```bash
    $ pip install git+https://github.com/Benjamin-Lee/MechWolf.git
```

## Updating MechWolf

Updating MechWolf is as easy as installing it. Just call `pip` with the
`--upgrade` flag:

```bash
    $ pip install mechwolf --upgrade
```
