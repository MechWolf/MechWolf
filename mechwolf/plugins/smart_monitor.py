from mechwolf import Apparatus, Sensor


def wrap_read(_read):
    async def inside():
        read = await _read()
        print("hi")
        return read

    return inside


def smart_monitor(apparatus: Apparatus):
    for sensor in apparatus[Sensor]:
        sensor._read = wrap_read(sensor._read)
