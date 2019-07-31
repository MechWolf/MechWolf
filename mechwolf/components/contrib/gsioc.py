class GsiocInterface(object):
    """
    An implementation of GSIOC serial communications protocol.

    GSIOC is used by many devices made by Gilson and other manufacturers.
    It runs on the RS-422/485 standard and works well with USB to RS-422
    adapters by FTDI, e.g. https://www.ftdichip.com/Products/Cables/USBRS422.htm

    For protocol details please see Gilson document LT2181: GSIOC Technical Manual.
    """

    metadata = {
        "author": [
            {
                "first_name": "Murat",
                "last_name": "Ozturk",
                "email": "muzcuk@gmail.com",
                "institution": "Indiana University, School of Informatics, Computing and Engineering",
                "github_username": "littleblackfish",
            }
        ],
        "stability": "beta",
        "supported": True,
    }

    def __init__(self, serial_port=None, unit_id=0):
        import aioserial

        self.ser = aioserial.AioSerial(
            serial_port, baudrate=19200, parity="E", stopbits=1, timeout=0.02
        )

        # Unit id encoding is offset by 128 per GSIOC specification
        self.gsioc_id = 0x80 + unit_id

    def identify(self):
        """Ask device to identify itself."""

        return self.immediate_command("%")

    async def reset(self):
        """Send standard reset command."""

        await self.immediate_command("$")

    def connect(self):
        """
        Connect to a GSIOC device

        Since GSIOC was designed around multiple slaves, even if we have
        a single device on the bus, we still have to 'connect' to a specific
        unit_id every time we send out a command.
        """

        # Disconnect all slaves
        self.ser.write([0xFF])
        self.ser.reset_input_buffer()

        # Connect slave with this ID
        max_try = 3
        for i in range(max_try):
            self.ser.write([self.gsioc_id])
            response = self.ser._read()
            if response == bytes([self.gsioc_id]):
                return True

        raise RuntimeError(
            f"Unable to connect device with GSIOC unit ID {self.gsioc_id - 128}. Check 'Unit ID' setting on device."
        )

    def immediate_command(self, command):
        """
        Send immediate command

        Immediate commands query GSIOC devices for information.
        """

        self.connect()

        self.ser.write(command.encode(encoding="ascii"))

        char = self.ser._read()

        response = b""
        while char < b"\x80":
            response += char
            # we ACK the character to get the next one
            self.ser.write([0x06])
            char = self.ser._read()

        # Shift the last char down by 128
        response += bytes([char[0] - 128])

        return response.decode(encoding="ascii")

    def buffered_command(self, command):
        """
        Send buffered command.

        Buffered commands send instructions to a slave device.

        """

        self.connect()

        # Making sure slave is ready
        echo = b""
        while echo != b"\n":
            self.ser.write(b"\n")
            echo = self.ser._read()

        if echo != b"\n":
            raise RuntimeError("GSIOC device not ready for buffered command.")

        # Command terminates with a \r
        for char in command + "\r":
            byte = char.encode(encoding="ascii")
            self.ser.write(byte)
            # Slave should echo each character back per GSIOC spec.
            echo = self.ser._read()

            if echo != byte:
                raise RuntimeError("GSIOC device did not respond to buffered command.")

    async def connect_async(self):
        """
        Async implementation of GsiocInterface.connect()
        """

        # Disconnect all slaves
        await self.ser.write_async([0xFF])
        self.ser.reset_input_buffer()

        # Connect slave with this ID
        max_try = 3
        for i in range(max_try):
            await self.ser.write_async([self.gsioc_id])
            response = await self.ser.read_async()
            if response == bytes([self.gsioc_id]):
                return True

        raise RuntimeError(
            "GSIOC device with ID {} did not respond.".format(self.gsioc_id - 128)
        )

    async def immediate_command_async(self, command):
        """
        Async implementation of GsiocInterface.immediate_command()
        """

        await self.connect_async()

        await self.ser.write_async(command.encode(encoding="ascii"))

        char = await self.ser.read_async()

        response = b""
        while char < b"\x80":
            response += char
            # we ACK the character to get the next one
            await self.ser.write_async([0x06])
            char = await self.ser.read_async()

        # Shift the last char down by 128
        response += bytes([char[0] - 128])

        return response.decode(encoding="ascii")

    async def buffered_command_async(self, command):
        """
        Async implementation of GsiocInterface.buffered_command()
        """

        await self.connect_async()

        # Making sure slave is ready
        echo = b""
        while echo != b"\n":
            await self.ser.write_async(b"\n")
            echo = await self.ser.read_async()

        if echo != b"\n":
            raise RuntimeError("GSIOC device not ready for buffered command.")

        # Command terminates with a \r
        for char in command + "\r":
            byte = char.encode(encoding="ascii")
            await self.ser.write_async(byte)
            # Slave should echo each character back per GSIOC spec.
            echo = await self.ser.read_async()

            if echo != byte:
                raise RuntimeError("GSIOC device did not respond to buffered command.")
