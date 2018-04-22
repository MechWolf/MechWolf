import click
from subprocess import call

@click.group()
def cli():
    pass

@cli.command(help="Do this before running hub or client!")
def setup():
    from scripts import config

@cli.command()
def hub():
    from scripts import hub

@cli.command()
def client():
    from scripts import client

if __name__ == '__main__':
    cli()
