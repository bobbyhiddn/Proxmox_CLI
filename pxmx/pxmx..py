import click
import importlib
import pkgutil
from configparser import ConfigParser
from pathlib import Path
from commands import commands_list

CONFIG_FILE_PATH = Path.home() / '.pxmx'

def load_config():
    """
    Load the configuration from the .pxmx file.
    """
    config = ConfigParser()
    if CONFIG_FILE_PATH.exists():
        config.read(CONFIG_FILE_PATH)
        return config['DEFAULT']
    else:
        return None

def create_config():
    """
    Prompt the user for Proxmox details and save them to the .pxmx file.
    """
    config = ConfigParser()
    config['DEFAULT'] = {
        'proxmox_ip': click.prompt("Enter the Proxmox IP or hostname"),
        'username': click.prompt("Enter the API username"),
        'password': click.prompt("Enter the password", hide_input=True),
    }
    
    with CONFIG_FILE_PATH.open('w') as configfile:
        config.write(configfile)

def get_or_create_config():
    """
    Load the config if it exists, otherwise create it.
    """
    config = load_config()
    if config is None:
        create_config()
        config = load_config()
    return config

@click.group()
@click.pass_context
def cli(ctx):
    """A Python CLI for utilizing the Proxmox API from the command line."""
    ctx.ensure_object(dict)
    ctx.obj['CONFIG'] = get_or_create_config()

def load_commands():
    """
    Dynamically load command modules from the commands directory.
    """
    commands_package = "commands"
    package = importlib.import_module(commands_package)
    prefix = package.__name__ + "."

    for _, modname, _ in pkgutil.iter_modules(package.__path__, prefix):
        module = importlib.import_module(modname)
        for attr in dir(module):
            if isinstance(getattr(module, attr), click.core.Command):
                cli.add_command(getattr(module, attr))

load_commands()

if __name__ == "__main__":
    cli(obj={})
