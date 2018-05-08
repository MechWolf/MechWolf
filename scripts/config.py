import re
import inspect
import os
import sys
import imp
import importlib.util
from collections import OrderedDict

from colorama import init, Fore, Back
import yaml
import requests
import click
from pick import pick
import rsa
import yamlordereddictloader
from serial.tools import list_ports
import keyring

import mechwolf as mw

# Only needed for hubs
try:
    from .get_cert import create_self_signed_cert
except ImportError:
    pass

# initialize colored printing
init(autoreset=True)

has_key = False
config_data = OrderedDict()
config_data["resolver_info"] = OrderedDict()
config_data["device_info"] = OrderedDict()

# Get the hub_id
hub_id = click.prompt("Welcome to MechWolf! What is your hub_id? If you don't have one, please choose one. (case sensitive)", type=str)
while requests.request("GET", mw.RESOLVER_URL + "get_hub", params={"hub_id":hub_id}).text != "failure: unable to locate":
    if click.confirm("This hub_id already exists. If you have previously set up a hub_id, please proceed. Proceed?", default=True):
        has_key = True
        break
    else:
        hub_id = click.prompt("Please select a new hub_id", type=str)
config_data["resolver_info"]["hub_id"] = hub_id

def get_key():
    security_key = click.prompt("You stated that you already have a hub_id. "\
                                "If so, you should already have a security_key. "\
                                "What is your key?",
                                type=str)
    if not mw.validate_security_key(security_key):
        raise ValueError("Invalid security_key.")
    return security_key


# Get the security_key
if has_key:
    try:
        security_key = keyring.get_password("mechwolf", "security_key")
        if security_key is None:
            security_key = get_key()
        else:
            print(f"Using security_key stored in keyring: {security_key}. If this is not correct the correct security key, run 'mechwolf update'.")
    except RuntimeError:
        config_data["device_info"]["security_key"] = get_key()
else:
    if click.confirm("Have you been issued a security key?", default=False):
        security_key = get_key()
    else:
        security_key = mw.generate_security_key()
        print(f"\nYour security key is {security_key}.")
        print(Fore.RED + "It is CRITICAL that this key be kept secret to prevent someone else from being able to control your synthesizer.")
        try:
            keyring.set_password("mechwolf", "security_key", security_key)
            print("It is stored in your secure keyring.\n")
        except RuntimeError:
            config_data["device_info"]["security_key"] = security_key
            print(Fore.RED + "It is store in your config file. Do not share this file!")

# Get the device type
device_type, _ = pick(["hub", "client"], "What kind of device is this?", indicator="->")

if device_type == "client":
    # get device name
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
            config[i[0]]  = pick([[port[0],port[1],port[2]] for port in list_ports.comports()][0], "Select the serial port your device is connected to:", indicator = '->')[0]
        else:
            config[i[0]] = click.prompt(i[0], type=i[1][0], default=i[1][1])
    config_data["device_info"]["device_settings"] = config

elif device_type == "hub":
    if has_key:
        # get public key
        rsa_private_filepath = click.prompt("RSA authentication private key filepath", type=str, default="./private.pem")
        with open(rsa_private_filepath, "rb") as f:
            rsa_private_filepath = os.path.realpath(f.name)
            data = f.read()
        try:
            rsa.PrivateKey.load_pkcs1(data)
        except:
            raise ValueError("Invalid Private Key File")

        # get private key
        rsa_public_filepath = click.prompt("RSA authentication public key filepath", type=str, default="./public.pem")
        with open(rsa_public_filepath, "rb") as f:
            rsa_public_filepath = os.path.realpath(f.name)
            data = f.read()
        try:
            rsa.PublicKey.load_pkcs1(data)
        except:
            raise ValueError("Invalid Public Key File")

    # if they don't have an RSA key, make one
    else:
        print("Now generating RSA authentication key for hub. This will allow your hub to prove its identity to the MechWolf resolver. This step may take a few seconds.")
        public, private = rsa.newkeys(2048)

        with open("public.pem", "wb+") as f:
            f.write(public.save_pkcs1())
            rsa_public_filepath = os.path.realpath(f.name)

        with open("private.pem", "wb+") as f:
            f.write(private.save_pkcs1())
            rsa_private_filepath = os.path.realpath(f.name)

    # store key location
    config_data["resolver_info"]["rsa_private_filepath"] = rsa_private_filepath
    config_data["resolver_info"]["rsa_public_filepath"] = rsa_public_filepath

    print("Now generating SSL certificate to encrypt communications between hub and client...")
    create_self_signed_cert()

# save the config file
yaml.dump(config_data, open(f"{device_type}_config.yml", "w+"), Dumper=yamlordereddictloader.Dumper, default_flow_style=False)
print(Fore.GREEN + f"\nSetup complete! When you're ready to start your {device_type}, run the following command:\n\n\t$ mechwolf {device_type}\n")
