import os
import shelve
import json
import yaml
import click
from click_didyoumean import DYMGroup
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


default_port = 5000
@cli.command(help="Run a MechWolf hub")
@click.option('-v', count=True, help="Verbose mode. Multiple -v options increase the verbosity. The maximum is 3.")
@click.option("-p", "--port", type=int, default=default_port, help=f"The port to serve the hub on. Defaults to {default_port}")
def hub(v, port):
    # set up the server
    from gevent.pywsgi import WSGIServer
    from scripts.hub import app
    http_server = WSGIServer(('', port), app)

    # alert the user, even when not in verbose mode
    click.secho(f"Hub started on 127.0.0.1:{port}!", fg="green")

    if not v:
        print("For more information, use the -v flag.")
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
