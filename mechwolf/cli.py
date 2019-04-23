import json
import os
import shelve

import click
import yaml
from click_didyoumean import DYMGroup

from . import mechwolf


@click.group(cls=DYMGroup)
def cli():
    pass

@cli.command(help="Convert a .db file into JSON or YAML")
@click.argument('db', type=click.Path(exists=True))
@click.option('--output', type=click.Choice(['yaml', 'json']), default="yaml", help="The file format to use")
def convert(db, output):
    db = os.path.splitext(db)[0]
    with shelve.open(db) as db:
        if output == "json":
            print(json.dumps(dict(db), indent=4))
        elif output == "yaml":
            print(yaml.dump(dict(db), default_flow_style=False))

@cli.command(help="Print the MechWolf version")
def version():
    print(mechwolf.__version__)


if __name__ == '__main__':
    cli()
