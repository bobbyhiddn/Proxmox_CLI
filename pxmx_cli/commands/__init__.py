import pkgutil
import importlib

__all__ = []
commands_list = []  # List to store command functions
aliases = {}  # Dictionary to store aliases

for _, module_name, _ in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    # Dynamically import the module
    _module = importlib.import_module('.' + module_name, __package__)
    # Here we retrieve the command function directly
    for item in dir(_module):
        if callable(getattr(_module, item)) and item != "click":
            commands_list.append(getattr(_module, item))
            break  # Assuming only one command per module
    # Collect aliases if present in the module
    if hasattr(_module, 'alias'):
        aliases[_module.alias] = vars(_module)[module_name]