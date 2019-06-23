import mechwolf as mw


def test_validate_component():
    # not a subclass of ActiveComponent
    class Test(mw.Component):
        def __init__(self):
            super().__init__()

    assert not mw.validate_component(Test())


def test_no_update_method():
    # doesn't have an update method
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)

        def base_state(self):
            pass

    assert not mw.validate_component(Test())


def test_no_update_dict():
    # base_state doesn't return a dictionary
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)

        def update(self):
            pass

        def base_state(self):
            pass

    assert not mw.validate_component(Test())


def test_empty_base_state():
    # base_state dictionary is not valid for the component because it's empty
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.active = False

        def update(self):
            pass

        def base_state(self):
            return {}

    assert not mw.validate_component(Test())


def test_invalid_base_state():
    # base_state dictionary is not valid for the component
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.active = False

        def update(self):
            pass

        def base_state(self):
            return dict(rate="10 mL")

    assert not mw.validate_component(Test())


def test_wrong_base_state_dimensionality():
    # base_state dictionary is wrong dimensionality
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.rate = mw.ureg.parse_expression("10 mL/min")

        def update(self):
            pass

        def base_state(self):
            return dict(rate="10 mL")

    assert not mw.validate_component(Test())


def test_passing_class():
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.active = False
            self.serial_port = serial_port

        def update(self):
            pass

        def base_state(self):
            return dict(active=False)

    # passing the class, not an instance
    assert not mw.validate_component(Test)


def test_base_state_type():
    # not right base_state value type
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.active = False
            self.serial_port = serial_port

        def update(self):
            pass

        def base_state(self):
            return dict(active="10 mL")

    assert not mw.validate_component(Test())

    # not right base_state value type
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.active = False
            self.serial_port = serial_port

        def update(self):
            pass

        def base_state(self):
            return "not a dict"

    assert not mw.validate_component(Test())


def test_validate_sensor_without_read():
    class Test(mw.Sensor):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.serial_port = serial_port

    assert not mw.validate_component(Test())


def test_validate_sensor_with_read():
    class Test(mw.Sensor):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.serial_port = serial_port

        def read():
            pass

    assert mw.validate_component(Test())
