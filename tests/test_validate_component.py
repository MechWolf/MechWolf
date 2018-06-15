import mechwolf as mw
import pytest

def test_validate_component():
    # not a subclass of ActiveComponent
    class Test(mw.Component):
        def __init__(self):
            super().__init__()
    assert mw.validate_component(Test()) == False

    # doesn't have an update method
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name="test1")
        def base_state(self):
            pass
        def config(self):
            pass
    assert mw.validate_component(Test()) == False

    # base_state doesn't return a dictionary
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name="test2")
        def update(self):
            pass
        def base_state(self):
            pass
        def config(self):
            pass
    assert mw.validate_component(Test()) == False

    # base_state dictionary is not valid for the component because it's empty
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name="test3")
            self.active = False
        def update(self):
            pass
        def base_state(self):
            return {}
        def config(self):
            pass
    assert mw.validate_component(Test()) == False

    # base_state dictionary is not valid for the component
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name="test4")
            self.active = False
        def update(self):
            pass
        def base_state(self):
            return dict(rate="10 mL")
        def config(self):
            pass
    assert mw.validate_component(Test()) == False

    # base_state dictionary is wrong dimensionality
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name="test5")
            self.rate = mw.ureg.parse_expression("10 mL/min")
        def update(self):
            pass
        def base_state(self):
            return dict(rate="10 mL")
        def config(self):
            pass
    assert mw.validate_component(Test()) == False

    # config doesn't return a dict
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name="test6")
            self.active = False
        def update(self):
            pass
        def base_state(self):
            return dict(active=False)
        def config(self):
            pass
    assert mw.validate_component(Test()) == False

    # config returns a dict
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name="test7")
            self.active = False
        def update(self):
            pass
        def base_state(self):
            return dict(active=False)
        def config(self):
            return {}
    assert mw.validate_component(Test()) == True

    # config dict is invalid due to variable mismatch
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name="test8")
            self.active = False
            self.serial_port = serial_port
        def update(self):
            pass
        def base_state(self):
            return dict(active=False)
        def config(self):
            return {"serial": (int, None)}
    assert mw.validate_component(Test()) == False

    # config dict is invalid due to value not being tuple
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name="test9")
            self.active = False
            self.serial_port = serial_port
        def update(self):
            pass
        def base_state(self):
            return dict(active=False)
        def config(self):
            return {"serial_port": int}
    assert mw.validate_component(Test()) == False

    # config dict is invalid due to being out of order
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name="test10")
            self.active = False
            self.serial_port = serial_port
        def update(self):
            pass
        def base_state(self):
            return dict(active=False)
        def config(self):
            return {"serial_port": (None, int)}
    assert mw.validate_component(Test()) == False

    # passing the class, not an instance
    assert mw.validate_component(Test) == False

    # not right base_state value type
    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name="test11")
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
            super().__init__(name="test12")
            self.active = False
            self.serial_port = serial_port
        def update(self):
            pass
        def base_state(self):
            return "not a dict"
        def config(self):
            return {"serial_port": (int, None)}
    assert mw.validate_component(Test()) == False

    class Test(mw.ActiveComponent):
        def __init__(self, serial_port=None):
            super().__init__(name="test13")
            self.active = False
            self.serial_port = serial_port
        def update(self):
            pass
        def base_state(self):
            return dict(active=False)
        def config(self):
            return {"serial_port": (int, None)}
    assert mw.validate_component(Test()) == True
