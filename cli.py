import os
import shelve
import json
import yaml
import click
import keyring
from scripts.client import run_client

@click.group()
def cli():
    pass

@cli.command(help="Do this before running a hub or client!")
def setup():
    from scripts import config

@cli.command(help="Run a MechWolf hub")
def hub():
    from gevent.pywsgi import WSGIServer
    from scripts.hub import app
    http_server = WSGIServer(('0.0.0.0', 443), app, keyfile='ssl.key', certfile='ssl.cert')
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
    run_client(verbosity=v, config=config)

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

if __name__ == '__main__':
    cli()
