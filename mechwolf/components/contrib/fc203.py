from ..stdlib.active_component import ActiveComponent

class GilsonFC203(ActiveComponent):
    """
    Controls a Gilson FC203B Fraction collector
    """

    metadata = {
        "author": [
            {
                "first_name": "Murat",
                "last_name": "Ozturk",
                "email": "hello@littleblack.fish",
                "institution": "Indiana University, School of Informatics, Computing and Engineering",
                "github_username": "littleblackfish",
            }
        ],
        "stability": "beta",
        "supported": True,
    }

    def __init__(self, name=None, serial_port=None, unit_id=1):
        super().__init__(name=name)

        self.serial_port = serial_port
        self.unit_id = unit_id
        self.position = 1
        self.prev_position = 1

    def __enter__(self):

        from .gsioc import GsiocInterface

        # create the serial connection
        self.gsioc = GsiocInterface(serial_port=self.serial_port, unit_id=self.unit_id)

        self.lock()
        self.gsioc.buffered_command("W1        MechWolf")
        self.gsioc.buffered_command("W2                ")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.gsioc.buffered_command("W1        MechWolf")
        self.gsioc.buffered_command("W2          Done!   ")
        self.unlock()
        del self.gsioc

    def lock(self):
        self.gsioc.buffered_command("L0")

    def unlock(self):
        self.gsioc.buffered_command("L1")

    async def goto(self, position):
        goto_command = "T" + str(int(position)).zfill(3)
        await self.gsioc.buffered_command_async(goto_command)
        await self.gsioc.buffered_command_async("W2       Collect " + str(position))

    async def drain(self, drain):
        """
        Switch to drain.

        This moves the head to the drain funnel.
        """

        if drain :
            self.prev_position = await self.gsioc.immediate_command_async('T')
            # Move head to drain rail
            # Note that this might contaminate samples.
            await self.gsioc.buffered_command_async("Y0000")
            await self.gsioc.buffered_command_async("W2         Drain")
        else :
            await self.goto(int(self.prev_position))

    async def divert(self, drain):
        """
        Activate diverter valve

        Activates the diverter valve.
        """

        if drain:
            await self.gsioc.buffered_command_async("V1")
        else :
            await self.gsioc.buffered_command_async("V0")

    async def update(self):

        await self.goto(self.position)

    def base_state(self):
        """We assume that the collector starts at the drain position.
        """
        return dict(position=1)
