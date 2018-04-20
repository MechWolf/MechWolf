from json import dumps, loads
import time

import aiohttp
import asyncio
import async_timeout
from colorama import init, Fore, Back, Style
import yaml
from vedis import Vedis
import requests
import itsdangerous

from mechwolf.components import *
import mechwolf as mw

# initialize colored printing
init(autoreset=True)

async def execute_procedure(protocol_id, procedure, session):
        await asyncio.sleep(procedure["time"])
        print(Fore.GREEN + f"executing: {procedure} at {time.time()}")
        me.update_from_params(procedure["params"])
        me.update()
        await log(session, dumps(dict(
                    protocol_id=protocol_id,
                    timestamp=time.time(),
                    success=True,
                    procedure=procedure)))

async def get_protocol(session):
    with db.transaction():
        server = db["server"]
    try:
        print(f"connecting to {server}")
        async with session.post(f"{server}/protocol", data=dict(device_id=DEVICE_NAME)) as resp:
            response = await resp.text()
            try:
                response = loads(response)
                return response["protocol_id"], response[DEVICE_NAME]
            except:
                return "", response


    except aiohttp.client_exceptions.ClientConnectorError:
        print(Fore.YELLOW + f"Unable to connect to {server}")
        resolve_server()
        return "", False

async def get_start_time(session):
    with db.transaction():
        server = db["server"]
    try:
        async with session.get(f"{server}/start_time", params=dict(device_id=DEVICE_NAME)) as resp:
            response = await resp.text()
            try:
                response = loads(response)
            except:
                pass
            return response

    # if the server is down, try again
    except aiohttp.client_exceptions.ClientConnectorError:
        print(Fore.YELLOW + f"Unable to connect to {server}. Trying again...")
        resolve_server()
        return False

async def log(session, data):
    with db.transaction():
        server = db["server"]
    try:
        async with session.post(f"{server}/log", json=data) as resp:
            await resp.text()
    except (aiohttp.client_exceptions.ClientConnectorError, aiohttp.client_exceptions.ClientOSError):
        with db.transaction():
            db.List("log").append(data)
        print(Fore.RED + f"Failed to log {data}. Saved to database.")
    return

async def main(loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        while True:
            # try to get a protocol
            protocol = "no protocol"
            while protocol == "no protocol":
                protocol_id, protocol = await get_protocol(session)
                print("No new protocol received.")
                time.sleep(5)
            if not protocol:
                time.sleep(5)
                continue
            print(Fore.GREEN + f"Proocol received: {protocol}")

            # once a protocol is received, try to get a start time
            start_time = await get_start_time(session)
            while start_time == "no start time":
                start_time = await get_start_time(session)
                print(Fore.YELLOW + "No start time received yet. Trying again in 5 seconds.")
                time.sleep(5)
            # if the server doesn't get hear from all active components, it will abort execution
            if start_time == "abort":
                print(Fore.RED + "Aborting upon command from server.")
                continue
            # handle connection failures
            if not start_time:
                time.sleep(5)
                continue
            # verify start time hasn't happened yet
            if start_time < time.time():
                print(Fore.RED + "Start time is in past. Aborting...")
                continue
            print(Fore.GREEN + f"Start time received: {start_time}")

            # wait until the beginning of the protocol
            time.sleep(start_time - time.time())

            # create futures for each procedure in the protocol and execute them
            coros = [execute_procedure(protocol_id, procedure, session) for procedure in protocol]
            await asyncio.gather(*coros)

            # upon completion, alert the user and begin the loop again
            print(Fore.GREEN + "Protocol executed successfully.")

            if len(db.List("log")):
                print("Submitting failed logs")
                resolve_server()
                for i in range(len(db.List("log"))):
                    await log(session, db.List("log").pop())

def resolve_server():
    server = ""
    while not server:
        response = requests.get(mw.RESOLVER_URL + "get_hub", params={"hub_id":HUB_ID})
        s = itsdangerous.Signer(SECURITY_KEY)
        server = s.unsign(response.json()["hub_address"]).decode()
        with db.transaction():
            db["server"] = f"http://{server}"
        # print("Finding server")
        # data, addr = s.recvfrom(1024) # wait for a packet
        # data = data.decode()
        # if data.startswith(KEY):
        #     server = f"http://{data[len(KEY):]}:5000"
        #     print(Fore.GREEN + f"Got service announcement from {server}")

db = Vedis("client.db") # set up db

# get the config data
with open("client_config.yml", "r") as f:
    config = yaml.load(f)
SECURITY_KEY = config['resolver_info']['security_key']
HUB_ID = config['resolver_info']['hub_id']
DEVICE_NAME = config["device_info"]["device_name"]

# default to cached server address
# try:
#     with db.transaction():
#         server = db["server"]
# except KeyError:
resolve_server()

# create the client object
class_type = globals()[config["device_info"]["device_class"]]

# get and execute protocols forever
with class_type(name=DEVICE_NAME, **config["device_info"]["device_settings"]) as me:

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

# with ViciValve(mapping = None,
#                   name = DEVICE_NAME,
#            serial_port = '/dev/tty.usbserial',
#              positions = 10) as me:
