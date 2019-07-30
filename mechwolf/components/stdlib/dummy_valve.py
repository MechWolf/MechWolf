from typing import Optional

from loguru import logger

from .valve import Valve


class DummyValve(Valve):
    """
    A fake valve, used internally for testing.

    ::: danger
    This component can be used in a real protocol, although it doesn't actually exist.
    :::

    Arguments:
    - `mapping`: The mapping from components to their integer port numbers.
    - `name`: The name of the valve.

    Attributes:
    - `mapping`: The mapping from components to their integer port numbers.
    - `name`: The name of the valve.
    - `setting`: The position of the valve as an int (mapped via `mapping`).
    """

    def __init__(self, name: Optional[str] = None, mapping: dict = {}):
        super().__init__(name=name, mapping=mapping)

    async def update(self) -> None:
        logger.trace(f"Switching {self.name} to position {self.setting}")
