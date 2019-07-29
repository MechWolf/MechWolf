from typing import Mapping, Optional

from .active_component import ActiveComponent, Component


class Valve(ActiveComponent):
    """
    A generic valve.

    Arguments:
    - `mapping`: The mapping from components to their integer port numbers.
    - `name`: The name of the valve.

    Attributes:
    - `mapping`: The mapping from components to their integer port numbers.
    - `name`: The name of the valve.
    - `setting`: The position of the valve as an int (mapped via `mapping`).
    """

    def __init__(
        self,
        mapping: Optional[Mapping[Component, int]] = None,
        name: Optional[str] = None,
    ):
        super().__init__(name=name)
        self.mapping = mapping
        self.setting = 1
        self._visualization_shape = "parallelogram"

    def base_state(self) -> dict:
        """
        Default to `setting=1`.

        This is an arbitrary choice but is guaranteed to be a valid setting.
        """
        return {"setting": 1}

    def validate(self, dry_run):
        if not self.mapping:
            raise ValueError(f"{self} requires a mapping. None provided.")
        return super().validate(dry_run)
