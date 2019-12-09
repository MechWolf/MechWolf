from mechwolf import Apparatus, Sensor
import aiohttp


def wrap_read(_read):
    async def inside():
        read = await _read()
        async with aiohttp.ClientSession() as session:
            async with session.post("http://0.0.0.0:5000", data={"data": read}) as resp:
                text = await resp.text()
                if text == "Error!":
                    raise RuntimeError("Anomaly detected!")
        return read

    return inside


def smart_monitor(apparatus: Apparatus):
    for sensor in apparatus[Sensor]:
        sensor._read = wrap_read(sensor._read)
