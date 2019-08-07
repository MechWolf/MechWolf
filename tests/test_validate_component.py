import pytest

import mechwolf as mw


def test_validate_component():
    # not a subclass of ActiveComponent, so it won't work
    class Test(mw.Component):
        def __init__(self):
            super().__init__()

    Test()._validate(dry_run=True)
    with pytest.raises(RuntimeError):
        Test()._validate(dry_run=False)


def test_empty_base_state():
    # base_state dictionary is not valid for the component because it's empty
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.active = False
            self._base_state = {}

        async def _update(self):
            return True

    with pytest.raises(ValueError):
        Test()._validate(dry_run=True)


def test_invalid_base_state():
    # base_state dictionary is not valid for the component
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.active = False
            self._base_state = dict(rate="10 mL")

        async def _update(self):
            return True

    with pytest.raises(ValueError):
        Test()._validate(dry_run=True)


def test_wrong_base_state_dimensionality():
    # base_state dictionary is wrong dimensionality
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.rate = mw._ureg.parse_expression("10 mL/min")
            self._base_state = dict(rate="10 mL")

        async def _update(self):
            return True

    with pytest.raises(ValueError):
        Test()._validate(dry_run=True)


def test_passing_class():
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.active = False
            self.serial_port = serial_port
            self._base_state = dict(active=False)

        async def _update(self):
            pass

    # should pass both as a dry run and as a real run (since update doesn't do anything)
    Test()._validate(dry_run=True)
    Test()._validate(dry_run=False)


def test_base_state_type():
    # not right base_state value type
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.active = False
            self.serial_port = serial_port
            self._base_state = dict(active="10 mL")

        async def _update(self):
            return True

    with pytest.raises(ValueError):
        Test()._validate(dry_run=True)

    # not right base_state value type
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.active = False
            self.serial_port = serial_port
            self._base_state = "not a dict"

        async def _update(self):
            return True

    with pytest.raises(ValueError):
        Test()._validate(dry_run=True)


def test_validate_sensor_without_read():
    class Test(mw.Sensor):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.serial_port = serial_port

    with pytest.raises(NotImplementedError):
        Test()._validate(dry_run=False)
    Test()._validate(dry_run=True)  # should pass during a dry run


def test_update_must_return_none():
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.active = False
            self._base_state = dict(active=False)

        async def _update(self):
            return False

    Test()._validate(dry_run=True)
    with pytest.raises(ValueError):
        Test()._validate(dry_run=False)


def test_default_update():
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.active = False
            self._base_state = dict(active=False)

    Test()._validate(dry_run=True)
    with pytest.raises(NotImplementedError):
        Test()._validate(dry_run=False)


def test_sync_update():
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.active = False
            self._base_state = dict(active=False)

        def _update(self):
            pass

    Test()._validate(dry_run=True)
    with pytest.raises(ValueError):
        Test()._validate(dry_run=False)


def test_sync_read():
    class Test(mw.Sensor):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.serial_port = serial_port

        def _read(self):
            return 1

        async def _update(self):
            pass

    Test()._validate(dry_run=True)
    with pytest.raises(ValueError):
        Test()._validate(dry_run=False)


def test_validate_sensor_with_failing_read():
    class Test(mw.Sensor):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.serial_port = serial_port

        async def _read(self):
            raise RuntimeError("This component is broken!")

        async def _update(self):
            pass

    Test()._validate(dry_run=True)
    with pytest.raises(RuntimeError):
        Test()._validate(dry_run=False)
