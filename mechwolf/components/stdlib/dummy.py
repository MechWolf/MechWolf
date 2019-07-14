from .component import ActiveComponent


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


class BrokenDummyComponent(Dummy):
    """
    A fake component, used internally for testing. Its `update()` method always returns `True` during a dry run but always returns `False` in a real run.

    ::: danger
    Using this component during real protocol execution will result in a failure.
    :::

    Attributes:
    - `active` (bool): Whether the component is active. This doesn't actually mean anything.
    """

    def __init__(self, name=None):
        super().__init__(name=name)

    def update(self):
        if self.active:
            return False
        else:
            return True

    def validate(self, dry_run):
        return True
