from .active_component import ActiveComponent


class Dummy(ActiveComponent):
    """
    A fake component, used internally for testing.

    ::: warning
    This component *can* be used in a non-dry run protocol execution. It does not do anything.
    :::

    Attributes:
    - `active` (bool): Whether the component is active. This doesn't actually mean anything.
    """

    def __init__(self, name=None):
        super().__init__(name=name)
        self.active = False

    def base_state(self) -> dict:
        return dict(active=False)

    def update(self) -> bool:
        if self.active:
            print("Active!")
        else:
            print("Inactive.")
        return True
