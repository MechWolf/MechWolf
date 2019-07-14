from typing import Optional

from .component import ActiveComponent


class Valve(ActiveComponent):
    """
    A generic valve.

    Attributes:
    - `mapping` (`dict`): The mapping from components to their integer port numbers.
    - `name` (`str`, optional): The name of the Valve.
    - `setting` (`int`): The position of the valve.
    """

    def __init__(self, mapping: dict, name: Optional[str] = None):
        super().__init__(name=name)
        self.mapping = mapping
        self.setting = 1
        self._visualization_shape = "parallelogram"

    def base_state(self) -> dict:
        """
        Default to the first setting.

        This is an arbitrary choice but is guaranteed to be a valid setting.
        """
        return {"setting": 1}
