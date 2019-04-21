import imp
import inspect
import os
import sys
from collections import OrderedDict

import click
import requests
import yaml
import yamlordereddictloader
from colorama import Back, Fore, init
from pick import pick
from serial.tools import list_ports

import mechwolf as mw

# initialize colored printing
init(autoreset=True)

has_key = False
config_data = OrderedDict()
config_data["resolver_info"] = OrderedDict()
config_data["device_info"] = OrderedDict()

# Get the hub_id
hub_id = click.prompt("Welcome to MechWolf! What is your hub_id? If you don't have one, please choose one. (case sensitive)", type=str)

device_name = click.prompt("Device name (case sensitive)", type=str)
config_data["device_info"]["device_name"] = device_name

# get device type
device_classes = ["Import from file"]
device_objs = [""]
for name, obj in inspect.getmembers(mw.components):
    try:
        if inspect.isclass(obj) and mw.validate_component(obj(name=name), warnings=False):
            device_classes.insert(0, obj.__name__)
            device_objs.insert(0, obj)
    except TypeError:
        pass
device_class, device_idx = pick(device_classes, "Which type of component is this?", indicator="->")

# handle user-created components
if device_class == "Import from file":
    device_class = click.prompt("Component name (e.g. ViciValve, VarianPump, etc.)", type=str)
    config_data["device_info"]["device_class"] = device_class

    # get filepath
    filepath = click.prompt("Component filepath", type=click.Path(exists=True))
    if not filepath.endswith(".py"):
        raise ValueError(Fore.RED + "Component filepath must be a .py file")
    with open(filepath) as f:
        absolute_path = os.path.realpath(f.name)
        config_data["device_info"]["device_class_filepath"] = absolute_path

    # get the component object
    module_name, _ = os.path.splitext(os.path.split(absolute_path)[-1])
    module = imp.load_source(module_name, absolute_path)
    device_obj = getattr(module, device_class)
    if not mw.validate_component(device_obj(name="validation_test")):
        raise RuntimeError(f"Component {device_class} is invalid.")

else:
    config_data["device_info"]["device_class"] = device_class
    device_obj = device_objs[device_idx]

# get device configuration
config = {}
for i in device_obj(name="setup").config().items():
    if i[0] == 'serial_port':
        ports = [port[0] for port in list_ports.comports()]
        ports.insert(0, '/dev/ttyUSB0')
        config[i[0]] = pick(ports, "If you are using a Raspberry Pi, we recommend you use /dev/ttyUSB0 as the serial port. Otherwise, select the serial port your device is connected to:", indicator='->')[0]
    else:
        config[i[0]] = click.prompt(i[0], type=i[1][0], default=i[1][1])
config_data["device_info"]["device_settings"] = config

# save the config file
yaml.dump(config_data, open(f"client_config.yml", "w+"), Dumper=yamlordereddictloader.Dumper, default_flow_style=False)
print(Fore.GREEN + f"\nSetup complete! When you're ready to start your client, run the following command:\n\n\t$ mechwolf client\n")
