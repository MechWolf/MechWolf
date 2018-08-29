from json import dumps, loads
from json.decoder import JSONDecodeError
import time
import shelve
import logging
import sys
import imp
import os

import aiohttp
import asyncio
# import async_timeout # pending removal
from colorama import init, Fore, Back, Style
import yaml
import requests
import itsdangerous
import keyring

from mechwolf.components import *
import mechwolf as mw

# initialize colored printing
init(autoreset=True)


async def execute_procedure(protocol_id, procedure, session, me):
    await asyncio.sleep(procedure["time"])
    logging.info(Fore.GREEN + f"Executing: {procedure} at {time.time()}" + Style.RESET_ALL)
    me.update_from_params(procedure["params"])
    async for result in me.update():
        if not isinstance(result, tuple):
            result = (result, time.time())
        results = dict(data=result[0],
                       protocol_id=protocol_id,
                       device_id=me.name,
                       timestamp=result[1],
                       procedure=procedure,
                       success=True)
        logging.debug(f"Logging {results} to hub")
        await log(session, dumps(results))

async def get_protocol(session):
    logging.debug("Attempting to get protocol")
    with shelve.open('client') as db:
        server = db["server"]
    try:
        logging.debug(f"Connecting to {server}")
        async with session.get(f"{server}/protocol", params=dict(device_id=timestamp_signer.sign(DEVICE_NAME).decode()), timeout=10) as resp:
            response = await resp.text()
            if response.startswith("no protocol"):
                return "", timestamp_signer.unsign(response, max_age=5).decode()
            response = loads(response)
            global serializer
            protocol = loads(
                serializer.loads(
                    response["protocol"]))[DEVICE_NAME]
            return response["protocol_id"], protocol

    except (aiohttp.client_exceptions.ClientError, asyncio.TimeoutError):
        logging.error(Fore.YELLOW + f"Unable to connect to {server}" + Style.RESET_ALL)
        resolve_server()

    except KeyError:
        logging.debug("New protocol issued to hub; no procedures for client.")

    return "", False

async def get_start_time(session):
    with shelve.open('client') as db:
        server = db["server"]
    try:
        logging.debug("Getting start time")
        async with session.get(f"{server}/start_time", params=dict(device_id=timestamp_signer.sign(DEVICE_NAME).decode())) as resp:
            response = await resp.text()
            response = timestamp_signer.unsign(response, max_age=5).decode()
            logging.debug(f"Got {response} as response to start time request")
            try:
                return float(response)
            except ValueError:  # if the response is "no start time"
                return response

    # if the server is down, try again
    except aiohttp.client_exceptions.ClientConnectorError:
        logging.error(
            Fore.YELLOW +
            f"Unable to connect to {server}. Trying again..." + Style.RESET_ALL)
        resolve_server()
        return False


async def log(session, data):
    with shelve.open('client') as db:
        server = db["server"]
    try:
        async with session.post(f"{server}/log", json={"data": serializer.dumps(data)}) as resp:
            await resp.text()
    except (aiohttp.client_exceptions.ClientConnectorError, aiohttp.client_exceptions.ClientOSError):
        with shelve.open('client') as db:
            try:
                db["log"] = db["log"] + [data]
            except KeyError:
                db["log"] = [data]
        logging.error(
            Fore.YELLOW +
            f"Failed to log {data}. Saved to database." + Style.RESET_ALL)
    return


async def main(loop, me):
    async with aiohttp.ClientSession(loop=loop, connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
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
            logging.info(Fore.GREEN + f"Protocol received: {protocol}" + Style.RESET_ALL)

            # once a protocol is received, try to get a start time
            start_time = await get_start_time(session)
            while start_time == "no start time":
                start_time = await get_start_time(session)
                logging.warning(
                    Fore.YELLOW +
                    "No start time received yet. Trying again in 5 seconds." + Style.RESET_ALL)
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
                    session,
                    me) for procedure in protocol]
            await asyncio.gather(*coros)

            # upon completion, alert the user and begin the loop again
            logging.info(Fore.GREEN + "Protocol executed successfully." + Style.RESET_ALL)

            # keep attempting to submit the failed logs
            try:
                with shelve.open('client') as db:
                    failed_submissions = db["log"]
                while len(failed_submissions):
                    logging.info("Submitting failed logs")
                    resolve_server()
                    with shelve.open('client') as db:
                        db["log"] = []
                    for i in failed_submissions:
                        await log(session, i)
            except KeyError:
                pass
            # don't lose data if the user exits
            except KeyboardInterrupt:
                with shelve.open('client') as db:
                    db["log"] = failed_submissions
                logging.critical("Shutting down")
                sys.exit()


def resolve_server():
    logging.info("Attempting to resolve server...")
    server = ""
    while not server:
        try:
            response = requests.get(
                mw.RESOLVER_URL + "get_hub",
                params={"hub_id": HUB_ID})
            logging.debug(f"Signed hub address from resolver: {response.json()['hub_address']}")
            server = signer.unsign(response.json()["hub_address"]).decode()
        except JSONDecodeError:
            raise RuntimeError(Fore.RED + "Invalid hub_id. Unable to resolve." + Style.RESET_ALL)
        except itsdangerous.BadSignature:
            raise RuntimeError(Fore.RED + "Invalid signature for hub_address." + Style.RESET_ALL)
        except requests.exceptions.ConnectionError:
            logging.warning(Fore.YELLOW + "No internet connection. Retrying in 10 seconds..." + Style.RESET_ALL)
            time.sleep(10)
            pass
        with shelve.open('client') as db:
            db["server"] = f"https://{server}"
        logging.info(f"New server resolved: {server}")


def run_client(config="client_config.yml"):
    # get the config data
    with open(config, "r") as f:
        config = yaml.load(f)

    # set up global variables
    global SECURITY_KEY
    try:
        SECURITY_KEY = keyring.get_password("mechwolf", "security_key")
    except:
        SECURITY_KEY = config["device_info"]["security_key"]
    global HUB_ID
    HUB_ID = config['resolver_info']['hub_id']
    global DEVICE_NAME
    DEVICE_NAME = config["device_info"]["device_name"]
    global signer
    signer = itsdangerous.Signer(SECURITY_KEY)
    global timestamp_signer
    timestamp_signer = itsdangerous.TimestampSigner(SECURITY_KEY)
    global serializer
    serializer = itsdangerous.URLSafeTimedSerializer(SECURITY_KEY)

    # find the server
    try:
        with shelve.open('client') as db:
            db["server"]
            logging.info(f"Cached server location found: {db['server']}")
    except KeyError:
        logging.info(f"No server location found")
        resolve_server()

    # create the client object
    try:
        class_type = globals()[config["device_info"]["device_class"]]
    except KeyError:
        logging.info("Unable to find component class in standard MechWolf library. Attempting to use user-provided component...")
        try:
            absolute_path = config["device_info"]["device_class_filepath"]
        except KeyError:
            logging.error(Fore.RED + "No component filepath given. If you are using a custom component, make sure to run mechwolf setup. If not using a custom component, ensure that device_class in client_config.yml is a valid MechWolf component." + Style.RESET_ALL)
            sys.exit()

        module_name, _ = os.path.splitext(os.path.split(absolute_path)[-1])
        module = imp.load_source(module_name, absolute_path)
        class_type = getattr(module, config["device_info"]["device_class"])

    # get and execute protocols forever
    with class_type(name=DEVICE_NAME, **config["device_info"]["device_settings"]) as me:

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop, me))


if __name__ == "__main__":
    run_client(verbosity=3)
