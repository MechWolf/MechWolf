from typing import Optional

from loguru import logger

from .valve import Valve


class DummyValve(Valve):
    """
    A fake valve, used internally for testing.

    ::: danger
    This component can be used in a real protocol, although it doesn't actually exist.
    :::

    Attributes:
    - `mapping` (`dict`): The mapping from components to their integer port numbers.
    - `name` (`str`, optional): The name of the Valve.
    - `setting` (`int`): The position of the valve.
    """

    def __init__(self, name: Optional[str] = None, mapping: dict = {}):
        super().__init__(name=name, mapping=mapping)

    def update(self):
        logger.trace(f"Switching {self.name} to position {self.setting}")
        return True
