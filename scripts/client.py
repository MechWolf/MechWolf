from json import dumps, loads
import time
import shelve
import logging
import sys

import aiohttp
import asyncio
import async_timeout
from colorama import init, Fore, Back, Style
import yaml
import requests
import itsdangerous

from mechwolf.components import *
import mechwolf as mw

# initialize colored printing
init(autoreset=True)


async def execute_procedure(protocol_id, procedure, session):
    await asyncio.sleep(procedure["time"])
    logging.info(Fore.GREEN + f"executing: {procedure} at {time.time()}")
    me.update_from_params(procedure["params"])
    me.update()
    await log(session, dumps(dict(
        protocol_id=protocol_id,
        timestamp=time.time(),
        success=True,
        procedure=procedure)))


async def get_protocol(session):
    logging.debug("attempting to get protocol")
    with shelve.open('client') as db:
        server = db["server"]
    try:
        logging.debug(f"connecting to {server}")
        async with session.get(f"{server}/protocol", params=dict(device_id=DEVICE_NAME)) as resp:
            response = await resp.text()
            if response.startswith("no protocol"):
                return "", timestamp_signer.unsign(response).decode()
            response = loads(response)
            protocol = loads(
                serializer.loads(
                    response["protocol"]))[DEVICE_NAME]
            return response["protocol_id"], protocol

    except aiohttp.client_exceptions.ClientConnectorError:
        logging.error(Fore.YELLOW + f"Unable to connect to {server}")
        resolve_server()
        return "", False


async def get_start_time(session):
    with shelve.open('client') as db:
        server = db["server"]
    try:
        logging.debug("Getting start time")
        async with session.get(f"{server}/start_time", params=dict(device_id=DEVICE_NAME)) as resp:
            response = await resp.text()
            response = timestamp_signer.unsign(response).decode()
            logging.debug(f"Got {response} as response to start time request")
            try:
                return float(response)
            except ValueError:  # if the response is "no start time"
                return response

    # if the server is down, try again
    except aiohttp.client_exceptions.ClientConnectorError:
        logging.error(
            Fore.YELLOW +
            f"Unable to connect to {server}. Trying again...")
        resolve_server()
        return False


async def log(session, data):
    with shelve.open('client') as db:
        server = db["server"]
    try:
        async with session.post(f"{server}/log", json=data) as resp:
            await resp.text()
    except (aiohttp.client_exceptions.ClientConnectorError, aiohttp.client_exceptions.ClientOSError):
        with shelve.open('client') as db:
            try:
                db["log"] = db["log"] + [data]
            except KeyError:
                db["log"] = [data]
        logging.error(
            Fore.YELLOW +
            f"Failed to log {data}. Saved to database.")
    return


async def main(loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        while True:
            # try to get a protocol
            protocol = "no protocol"
            while protocol == "no protocol":
                protocol_id, protocol = await get_protocol(session)
                logging.info("No new protocol received.")
                time.sleep(5)
            if not protocol:
                time.sleep(5)
                continue
            logging.info(Fore.GREEN + f"Protocol received: {protocol}")

            # once a protocol is received, try to get a start time
            start_time = await get_start_time(session)
            while start_time == "no start time":
                start_time = await get_start_time(session)
                logging.warning(
                    Fore.YELLOW +
                    "No start time received yet. Trying again in 5 seconds.")
                time.sleep(5)
            # if the server doesn't get hear from all active components, it
            # will abort execution
            if start_time == "abort":
                logging.info("Aborting upon command from server.")
                continue
            # handle connection failures
            if not start_time:
                time.sleep(5)
                continue
            # verify start time hasn't happened yet
            if start_time < time.time():
                logging.error(Fore.RED + "Start time is in past. Aborting...")
                continue
            logging.info(Fore.GREEN + f"Start time received: {start_time}")

            # wait until the beginning of the protocol
            time.sleep(start_time - time.time())

            # create futures for each procedure in the protocol and execute
            # them
            coros = [
                execute_procedure(
                    protocol_id,
                    procedure,
                    session) for procedure in protocol]
            await asyncio.gather(*coros)

            # upon completion, alert the user and begin the loop again
            logging.info(Fore.GREEN + "Protocol executed successfully.")

            # keep attempting to submit the failed logs
            with shelve.open('client') as db:
                try:
                    while len(db["log"]):
                        logging.info("Submitting failed logs")
                        resolve_server()
                        failed_submissions = db["log"]
                        db["log"] = []
                        for i in failed_submissions:
                            await log(session, failed_submissions[i])
                except KeyError:
                    pass
                # don't lose data if the user exits
                except KeyboardInterrupt:
                    db["log"] = failed_submissions
                    sys.exit()


def resolve_server():
    server = ""
    while not server:
        response = requests.get(
            mw.RESOLVER_URL +
            "get_hub",
            params={
                "hub_id": HUB_ID})
        server = signer.unsign(response.json()["hub_address"]).decode()
        with shelve.open('client') as db:
            db["server"] = f"http://{server}"
        # print("Finding server")
        # data, addr = s.recvfrom(1024) # wait for a packet
        # data = data.decode()
        # if data.startswith(KEY):
        #     server = f"http://{data[len(KEY):]}:5000"
        #     print(Fore.GREEN + f"Got service announcement from {server}")


def run_client(verbosity=0, config="client_config.yml"):
    # get the config data
    with open(config, "r") as f:
        config = yaml.load(f)

    # set up global variables
    global SECURITY_KEY
    SECURITY_KEY = config['resolver_info']['security_key']
    global HUB_ID
    HUB_ID = config['resolver_info']['hub_id']
    global DEVICE_NAME
    DEVICE_NAME = config["device_info"]["device_name"]
    global signer
    signer = itsdangerous.Signer(SECURITY_KEY)
    global timestamp_signer
    timestamp_signer = itsdangerous.TimestampSigner(SECURITY_KEY)
    global serial
    serializer = itsdangerous.URLSafeTimedSerializer(SECURITY_KEY)

    # set up logging
    verbosity_dict = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG}
    logging.basicConfig(level=verbosity_dict[verbosity])

    # find the server
    with shelve.open('client') as db:
        try:
            db["server"]
        except KeyError:
            resolve_server()

    # create the client object
    class_type = globals()[config["device_info"]["device_class"]]

    # get and execute protocols forever
    with class_type(name=DEVICE_NAME, **config["device_info"]["device_settings"]) as me:

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop))


if __name__ == "__main__":
    run_client(verbosity=3)
