from components import Test

from json import dumps, loads
import time
from sched import scheduler

import requests
import aiohttp
import asyncio
import async_timeout
from colorama import init, Fore, Back, Style

# initialize colored printing
init(autoreset=True)

DEVICE_NAME = "test_1"
me = Test(name=DEVICE_NAME)

# print(requests.post("http://127.0.0.1:5000/log", json=dumps(dict(time=time()))).text)
# print(requests.post("http://127.0.0.1:5000/protocol", data=dict(device_id=DEVICE_NAME)).text)

async def execute_procedure(procedure, session):
        await asyncio.sleep(procedure["time"])
        print(Fore.GREEN + f"executing: {procedure} at {time.time()}")
        me.update_from_params(procedure["params"])
        me.update()
        await log(session, dumps(dict(timestamp=time.time(), success=True, procedure=procedure)))

        
async def get_protocol(session):
    async with session.post("http://127.0.0.1:5000/protocol", data=dict(device_id=DEVICE_NAME)) as resp:
        response = await resp.text()
        try:
            response = loads(response)
        except:
            pass
        return response

async def get_start_time(session):
    async with session.get("http://127.0.0.1:5000/start_time", params=dict(device_id=DEVICE_NAME)) as resp:
        response = await resp.text()
        try:
            response = loads(response)
        except:
            pass
        return response

async def log(session, json):
    async with session.post("http://127.0.0.1:5000/log", json=json) as resp:
        return await resp.text()

async def main(loop):

    async with aiohttp.ClientSession(loop=loop) as session:
        while True:
            protocol = await get_protocol(session)
            while protocol == "no protocol":
                protocol = await get_protocol(session)
                time.sleep(5)

            print(Fore.GREEN + f"protocol accepted: {protocol}")

            start_time = await get_start_time(session)
            while start_time == "no start time":
                start_time = await get_start_time(session)
                time.sleep(5)

            print(Fore.GREEN + f"start time accepted: {start_time}")

            if start_time < time.time():
                print(Fore.RED + "start time is in past. Aborting...")
                time.sleep(5)

            time.sleep(start_time - time.time())

            coros = []
            for procedure in protocol:
                coros.append(execute_procedure(procedure,session))
            await asyncio.gather(*coros)
            print("done with protocol")

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))