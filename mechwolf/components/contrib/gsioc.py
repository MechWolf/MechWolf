from loguru import logger


class GsiocInterface(object):
    """
    An implementation of GSIOC serial communications protocol.

    ::: warning This is not an ActiveComponent.

    It is a helper class designed to make working with GSIOC components easier.
    You cannot add it to an [`Apparatus`](/api/core/apparatus/).
    It must be only be manipulated by other components.

    :::

    GSIOC is used by many devices made by Gilson and other manufacturers.
    It runs on the RS-422/485 standard and works well with USB to RS-422 adapters by FTDI, *e.g.* <https://www.ftdichip.com/Products/Cables/USBRS422.htm>.

    For protocol details please see Gilson document LT2181: GSIOC Technical Manual.

    Arguments:
    - `serial_port`: The serial port to connect over.
    - `unit_id`: The component's unit ID.

    Attributes:
    - `gsioc_id`: The `unit_id`, shifted down by 128 per the GSIOC specification.
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

        self._ser = aioserial.AioSerial(
            serial_port, baudrate=19200, parity="E", stopbits=1, timeout=0.02
        )

        # Unit id encoding is offset by 128 per GSIOC specification
        self.gsioc_id = 0x80 + unit_id

    def __repr__(self):
        return f"<{self}>"

    def __str__(self):
        return f"GsiocInterface {self.gsioc_id - 0x80} on port {self.serial_port}"

    def connect(self):
        """
        Connect to a GSIOC device.

        Since GSIOC was designed around multiple slaves, even if we have single device on the bus, we still have to 'connect' to a specific unit_id every time we send out a command.

        Raises:
        - `RuntimeError`: When unable to connect.
        """
        logger.trace(f"Connecting sync to {self}.")

        # Disconnect all slaves
        self._ser.write([0xFF])
        self._ser.reset_input_buffer()

        # Connect slave with this ID
        max_try = 3
        for i in range(max_try):
            logger.trace(f"Try {i+1}/{max_try}...")
            self._ser.write([self.gsioc_id])

            response = self._ser.read()
            logger.trace(f"Got {response}, expected {self.gsioc_id}.")

            if response == bytes([self.gsioc_id]):
                logger.trace(f"Connection to {self} successful.")
                return True

            logger.trace("Connection attempt failed.")

        raise RuntimeError(
            f"Unable to connect to device with GSIOC unit ID {self.gsioc_id - 128}. "
            f"Check 'Unit ID' setting on device."
        )

    async def connect_async(self) -> None:
        """
        Connect asynchronously to a GSIOC device.

        For API docs, see [`connect`](#connect)
        """
        logger.trace(f"Connecting async to {self}.")

        # Disconnect all slaves
        await self._ser.write_async([0xFF])
        self._ser.reset_input_buffer()

        # Connect slave with this ID
        max_try = 3
        for i in range(max_try):
            logger.trace(f"Try {i+1}/{max_try}...")
            await self._ser.write_async([self.gsioc_id])

            response = await self._ser.read_async()
            logger.trace(f"Got {response}, expected {self.gsioc_id}.")

            if response == bytes([self.gsioc_id]):
                logger.trace(f"Connection to {self} successful.")
                return

            logger.trace("Connection attempt failed.")

        raise RuntimeError(
            f"Unable to connect asynchronously to device with GSIOC unit ID "
            f"{self.gsioc_id - 128}. Check 'Unit ID' setting on device."
        )

    def immediate_command(self, command: str) -> str:
        """
        Send immediate command.

        Immediate commands query GSIOC devices for information.

        Arguments:
        - `command`: The command to execute.

        Returns:
        - The return value of the command.
        """

        logger.trace(f"Writing immediate command '{command}'.")
        self.connect()

        self._ser.write(command.encode(encoding="ascii"))

        char = self._ser.read()

        response = b""
        while char < b"\x80":
            response += char
            # we ACK the character to get the next one
            self._ser.write([0x06])
            char = self._ser.read()

        # Shift the last char down by 128
        response += bytes([char[0] - 128])

        logger.trace(f"Got response '{response.decode(encoding='ascii')}'.")
        return response.decode(encoding="ascii")

    async def immediate_command_async(self, command: str) -> str:
        """
        Async implementation of [`immediate_command`](#immediate-command).

        For API docs, see [`immediate_command`](#immediate-command).
        """

        logger.trace(f"Writing immediate command '{command}' async.")
        await self.connect_async()

        await self._ser.write_async(command.encode(encoding="ascii"))

        char = await self._ser.read_async()

        response = b""
        while char < b"\x80":
            response += char
            # we ACK the character to get the next one
            await self._ser.write_async([0x06])
            char = await self._ser.read_async()

        # Shift the last char down by 128
        response += bytes([char[0] - 128])

        logger.trace(f"Got response '{response.decode(encoding='ascii')}'.")
        return response.decode(encoding="ascii")

    def buffered_command(self, command: str) -> None:
        """
        Send buffered command.

        Buffered commands send instructions to a slave device.

        Arguments:
        - `command`: The command to execute.

        Raises:
        - `RuntimeError`: When the device is not ready or does not respond.
        """

        logger.trace(f"Sending command '{command}'.")
        self.connect()

        # Making sure slave is ready
        echo = b""
        while echo != b"\n":
            self._ser.write(b"\n")
            echo = self._ser.read()

        if echo != b"\n":
            logger.debug(
                f"Did not get expected response of '\\n' but "
                f"rather '{echo.decode(encoding='ascii')}'."
            )
            raise RuntimeError("GSIOC device not ready for buffered command.")

        # Command terminates with a \r
        for char in command + "\r":
            byte = char.encode(encoding="ascii")
            self._ser.write(byte)
            # Slave should echo each character back per GSIOC spec.
            echo = self._ser.read()

            if echo != byte:
                logger.debug(
                    f"Expected '{byte.decode(encoding='ascii')}', "
                    f"got '{echo.decode(encoding='ascii')}'."
                )
                raise RuntimeError("GSIOC device did not respond to buffered command.")

        logger.trace("Command sent successfully.")

    async def buffered_command_async(self, command: str) -> None:
        """
        Async implementation of [`buffered_command`](#buffered-command).

        For API docs, see [`buffered_command`](#buffered-command).
        """

        logger.trace(f"Sending command '{command}' async.")
        await self.connect_async()

        # Making sure slave is ready
        echo = b""
        while echo != b"\n":
            await self._ser.write_async(b"\n")
            echo = await self._ser.read_async()

        if echo != b"\n":
            logger.debug(
                f"Did not get expected response of '\\n' but rather "
                f"'{echo.decode(encoding='ascii')}'."
            )
            raise RuntimeError("GSIOC device not ready for buffered command.")

        # Command terminates with a \r
        for char in command + "\r":
            byte = char.encode(encoding="ascii")
            await self._ser.write_async(byte)
            # Slave should echo each character back per GSIOC spec.
            echo = await self._ser.read_async()

            if echo != byte:
                logger.debug(
                    f"Expected '{byte.decode(encoding='ascii')}', "
                    f"got '{echo.decode(encoding='ascii')}'."
                )
                raise RuntimeError("GSIOC device did not respond to buffered command.")

        logger.trace("Command sent successfully.")
