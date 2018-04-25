import click

from scripts.client import run_client

@click.group()
def cli():
    pass

@cli.command(help="Do this before running a hub or client!")
def setup():
    from scripts import config

@cli.command(help="Run a MechWolf hub")
def hub():
    from scripts import hub

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

if __name__ == '__main__':
    cli()
