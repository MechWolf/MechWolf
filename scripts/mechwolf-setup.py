from colorama import init, Fore, Back, Style
import yaml
from vedis import Vedis
import requests
from mechwolf import RESOLVER_URL, generate_security_key
import click
import re

# initialize colored printing
init(autoreset=True)

has_key = False

# Get the hub_id
print(
    "\nWelcome to MechWolf!\n\n"\
    "To begin, what is your hub_id? If you don't have one, please choose one.\n")
hub_id = click.prompt("hub_id", type=str)
while requests.request("GET", RESOLVER_URL + "get_hub", params={"hub_id":hub_id}).text != "request failed: unable to locate":
    if click.confirm("This hub_id already exists. If you have previously set up a hub_id, please proceed. Proceed?", default=True):
        has_key = True
        break
    else:
        hub_id = click.prompt("Please select a new hub_id", type=str)

# Get the security_key
if has_key:
    security_key = click.prompt("You stated that you already have a hub_id. "\
                                "If so, you should already have a security_key. "\
                                "What is your key?",
                                type=str)
    if not re.match(r"\w*-\w*-\w*-\w*-\w*-\w*", security_key):
        raise ValueError("Invalid security_key.")
else:
    security_key = generate_security_key()
    print("\nYour security key is "\
          + Back.YELLOW + Fore.BLACK + f"{security_key}", end="")
    print(".\n")
    print(Fore.RED + "It is CRITICAL that this key be kept secret to prevent someone else from being able to control your synthesizer.")
    print("Please store this key somewhere safe.\n")

# Get the device type
device_type = ""
while device_type.lower() not in ["hub", "client"]:
    device_type = input("What kind of device is this? [hub/client] ")
