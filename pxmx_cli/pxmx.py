#!/usr/bin/env python3

import click
from configparser import ConfigParser
from pathlib import Path

# Assuming commands are in a subpackage or directory named 'commands'
from pxmx_cli.commands import commands_list, aliases

CONFIG_FILE_PATH = Path.home() / '.pxmx'

def ensure_config():
    """Ensure configuration file exists and return its contents."""
    config = ConfigParser()
    if not CONFIG_FILE_PATH.exists() or not config.read(CONFIG_FILE_PATH):
        print("Configuring pxmx for the first time...")
        proxmox_ip = click.prompt("Enter the Proxmox IP or hostname")
        username = click.prompt("Enter the API username")
        password = click.prompt("Enter the password", hide_input=True)

        config['DEFAULT'] = {'proxmox_ip': proxmox_ip, 'username': username, 'password': password}

        with CONFIG_FILE_PATH.open('w') as configfile:
            config.write(configfile)
    else:
        config.read(CONFIG_FILE_PATH)

    return config['DEFAULT']

@click.group()
@click.pass_context
def cli(ctx):
    """A Python CLI for utilizing the Proxmox API from the command line."""
    ctx.obj = ensure_config()

# Dynamically load commands
print(commands_list)  # Add this to see what's being added to cli
for command in commands_list:
    cli.add_command(command)


@cli.command()
@click.pass_obj 
def config(config):
    """Display the current configuration."""
    print(f"Proxmox IP: {config['proxmox_ip']}")
    print(f"Username: {config['username']}")

@cli.command()
@click.pass_obj
def pxmx(config):
    """Display the current commands."""

    # Print the available commands
    print("\nAvailable commands:")
    for command in commands_list:
        print(f"  {command.name}")

    print("\nAvailable aliases:")
    for alias, command in aliases.items():
        print(f"  {alias}: {command.name}")

if __name__ == "__main__":
    cli()
