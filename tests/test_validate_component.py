import mechwolf as mw
import pytest

def test_validate():
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
    assert mw.validate_component(Test()) == False

    # base_state doesn't return a dictionary
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name="test2")
        def update(self):
            pass
        def base_state(self):
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
    assert mw.validate_component(Test()) == False

    # is good to go
    class Test(mw.ActiveComponent):
        def __init__(self):
            super().__init__(name="test6")
            self.active = False
        def update(self):
            pass
        def base_state(self):
            return dict(active=False)

    assert mw.validate_component(Test()) == True
