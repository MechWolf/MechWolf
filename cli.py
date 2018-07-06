import os
import shelve
import json
import yaml
import click
from click_didyoumean import DYMGroup
import keyring
import logging
import mechwolf

def set_verbosity(v):
    # set up logging
    verbosity_dict = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG}
    logging.basicConfig(level=verbosity_dict[v])

@click.group(cls=DYMGroup)
def cli():
    pass

@cli.command(help="Do this before running a hub or client!")
def setup():
    from scripts import config

@cli.command(help="Run a MechWolf hub")
@click.option('-v', count=True, help="Verbose mode. Multiple -v options increase the verbosity. The maximum is 3.")
def hub(v):
    # set up the server
    from gevent.pywsgi import WSGIServer
    from scripts.hub import app
    http_server = WSGIServer(('0.0.0.0', 443), app, keyfile='ssl.key', certfile='ssl.cert')

    # alert the user, even when not in verbose mode
    if not v:
        print("Hub started! For more information, use the -v flag.")
    set_verbosity(v)

    # start the server
    http_server.serve_forever()

@cli.command(help="Run a MechWolf client")
@click.option('-v', count=True, help="Verbose mode. Multiple -v options increase the verbosity. The maximum is 3.")
@click.option(
    '-c',
    '--config',
    type=click.Path(resolve_path=True, exists=True, dir_okay=False),
    default="client_config.yml",
    help="The configuration file for the client")
def client(v, config):
    set_verbosity(v)
    from scripts.client import run_client
    run_client(config=config)

@cli.command(help="Update the stored hub_id and security_key")
@click.option('-h', '--hub_id', prompt=True, default=lambda: keyring.get_password("mechwolf", "hub_id"))
@click.option('-s', "--security_key", prompt=True, default=lambda: keyring.get_password("mechwolf", "security_key"))
def update(hub_id, security_key):
    keyring.set_password("mechwolf", "hub_id", hub_id)
    keyring.set_password("mechwolf", "security_key", security_key)

@cli.command(help="Convert a .db file into JSON or YAML")
@click.argument('db', type=click.Path(exists=True))
@click.option('--output', type=click.Choice(['yaml', 'json']), prompt=True, default="yaml", help="The file format to use")
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
