from components import ViciValve, Valve

from json import dumps, loads
import time
from socket import socket, AF_INET, SOCK_DGRAM

import aiohttp
import asyncio
import async_timeout
from colorama import init, Fore, Back, Style
import yaml

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
    try:
        async with session.post(f"{SERVER}/protocol", data=dict(device_id=DEVICE_NAME)) as resp:
            response = await resp.text()
            try:
                response = loads(response)
                return response["protocol_id"], response[DEVICE_NAME]
            except:
                return "", response
    

    except aiohttp.client_exceptions.ClientConnectorError:
        print(Fore.YELLOW + "Unable to connect to server.")
        find_server()
        return "", False

async def get_start_time(session):
    try:
        async with session.get(f"{SERVER}/start_time", params=dict(device_id=DEVICE_NAME)) as resp:
            response = await resp.text()
            try:
                response = loads(response)
            except:
                pass
            return response

    # if the server is down, try again
    except aiohttp.client_exceptions.ClientConnectorError:
        print(Fore.YELLOW + "Unable to connect to server. Trying again...")
        return "no start time"

async def log(session, json):
    async with session.post(f"{SERVER}/log", json=json) as resp:
        return await resp.text()

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

def find_server():
    # https://stackoverflow.com/questions/21089268/python-service-discovery-advertise-a-service-across-a-local-network
    s = socket(AF_INET, SOCK_DGRAM) # create UDP socket
    s.bind(('', PORT))

    global SERVER
    SERVER = ""
    while not SERVER:
        print("Finding server")
        data, addr = s.recvfrom(1024) # wait for a packet
        data = data.decode()
        if data.startswith(KEY):
            SERVER = f"http://{data[len(KEY):]}:5000"
            print(Fore.GREEN + f"Got service announcement from {SERVER}")

# placeholder global variable
SERVER = ""

# read the config file
config = yaml.load(open('client_config.yaml', 'r'))
DEVICE_NAME = config["device_info"]["device_name"]
PORT = config["network_info"]["port"]
KEY = config["network_info"]["key"] # to make sure we don't confuse or get confused by other programs

# create the client object
class_type = globals()[config["device_info"]["class"]]
me = class_type(name=DEVICE_NAME)

# locate the server address
find_server()

# get and execute protocols forever
loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))


# with ViciValve(mapping = None,
#                   name = DEVICE_NAME,
#            serial_port = '/dev/tty.usbserial',
#              positions = 10) as me: