import mechwolf as mw
import pytest

def test_validate_component():
    # not a subclass of ActiveComponent
    class Test(mw.Component):
        def __init__(self):
            super().__init__()
    assert mw.validate_component(Test()) == False

def test_no_update_method():
    # doesn't have an update method
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)

        def base_state(self):
            pass

        def config(self):
            pass
    assert mw.validate_component(Test()) == False

def test_no_update_dict():
    # base_state doesn't return a dictionary
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)

        def update(self):
            pass

        def base_state(self):
            pass

        def config(self):
            pass
    assert mw.validate_component(Test()) == False

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

        def config(self):
            pass
    assert mw.validate_component(Test()) == False

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

        def config(self):
            pass
    assert mw.validate_component(Test()) == False

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

        def config(self):
            pass
    assert mw.validate_component(Test()) == False

def test_config_doesnt_return_dict():
    # config doesn't return a dict
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.active = False

        def update(self):
            pass

        def base_state(self):
            return dict(active=False)

        def config(self):
            pass
    assert mw.validate_component(Test()) == False

def test_valid_component_no_config_required():
    # config returns a dict
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name=None)
            self.active = False

        def update(self):
            pass

        def base_state(self):
            return dict(active=False)

        def config(self):
            return {}
    assert mw.validate_component(Test()) == True

def test_config_dict_mismatch():
    # config dict is invalid due to variable mismatch
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.active = False
            self.serial_port = serial_port

        def update(self):
            pass

        def base_state(self):
            return dict(active=False)

        def config(self):
            return {"serial": (int, None)}
    assert mw.validate_component(Test()) == False

def test_invalid_config_dict_value_type():
    # config dict is invalid due to value not being tuple
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.active = False
            self.serial_port = serial_port

        def update(self):
            pass

        def base_state(self):
            return dict(active=False)

        def config(self):
            return {"serial_port": int}
    assert mw.validate_component(Test()) == False

def test_invalid_config_dict_value_order():
    # config dict is invalid due to being out of order
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.active = False
            self.serial_port = serial_port

        def update(self):
            pass

        def base_state(self):
            return dict(active=False)

        def config(self):
            return {"serial_port": (None, int)}
    assert mw.validate_component(Test()) == False

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

        def config(self):
            return {"serial_port": (None, int)}
    # passing the class, not an instance
    assert mw.validate_component(Test) == False

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

        def config(self):
            return {"serial_port": (int, None)}
    assert mw.validate_component(Test()) == False

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

        def config(self):
            return {"serial_port": (int, None)}
    assert mw.validate_component(Test()) == False

def test_valid_component_config_required():
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.active = False
            self.serial_port = serial_port

        def update(self):
            pass

        def base_state(self):
            return dict(active=False)

        def config(self):
            return {"serial_port": (int, None)}
    assert mw.validate_component(Test()) == True

def test_validate_sensor_without_read():
    class Test(mw.Sensor):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.serial_port = serial_port

        def config(self):
            return {"serial_port": (int, None)}
    assert mw.validate_component(Test()) == False

def test_validate_sensor_with_read():
    class Test(mw.Sensor):
        def __init__(self, serial_port=None):
            super().__init__(name=None)
            self.serial_port = serial_port

        def read():
            pass

        def config(self):
            return {"serial_port": (int, None)}
    assert mw.validate_component(Test()) == True
