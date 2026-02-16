import asyncio

import click

from api.cli.create_user import _create_user


@click.group()
def main():
    pass


@main.command()
@click.argument("email")
@click.argument("fullname")
@click.option(
    "--username", default=None, help="Define a username or let the system create one"
)
@click.option(
    "--password", default=None, help="Define a password or let the system create one"
)
@click.option("--admin", is_flag=True, help="The user is admin")
def create_user(email, fullname, username, password, admin):
    asyncio.run(_create_user(email, fullname, username, password, admin))
