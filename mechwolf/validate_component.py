from . import term, ureg
from .components import ActiveComponent, Sensor


def validate_component(component, warnings=True):
    """Checks if a component's class is valid.

    Arguments:
        component (Component): The component being validated.
        warnings (bool): Whether to show warnings when validating. Defaults to true.

    Returns:
        bool: True if valid, else False.
    """

    # ensure is instance, not class
    if isinstance(component, type):
        if warnings:
            print(term.red(f"{component} is a class, not an instance of one."))
        return False

    # ensure is an ActiveComponent
    if not issubclass(component.__class__, ActiveComponent):
        if warnings:
            print(term.red(f"{component} is not an instance of ActiveComponent"))
        return False

    # must have an update method
    elif not callable(getattr(component, "update", None)):
        if warnings:
            print(term.red(f"{component} does not have an update method"))
        return False

    # must have a base_state method
    elif not callable(getattr(component, "base_state", None)):
        if warnings:
            print(term.red(f"{component} does not have a base_state method"))
        return False

    # the base_state dict must not be empty
    elif not component.base_state():
        if warnings:
            print(term.red("base_state method dict must not be empty"))
        return False

    # base_state method must return a dict
    elif not isinstance(component.base_state(), dict):
        if warnings:
            print(term.red("base_state method does not return a dict"))
        return False

    # validate the base_state dict
    for k, v in component.base_state().items():
        if not hasattr(component, k):
            if warnings:
                print(
                    term.red(
                        f"Invalid attribute {k} for {component}. Valid attributes are {component.__dict__}"
                    )
                )
            return False
        if (
            isinstance(component.__dict__[k], ureg.Quantity)
            and ureg.parse_expression(v).dimensionality
            != component.__dict__[k].dimensionality
        ):
            if warnings:
                print(
                    term.red(
                        f"Invalid dimensionality {ureg.parse_expression(v).dimensionality} for {k} for {component}."
                    )
                )
            return False
        elif not isinstance(component.__dict__[k], ureg.Quantity) and not isinstance(
            component.__dict__[k], type(v)
        ):
            if warnings:
                print(
                    term.red(
                        f"Bad type matching for {k} in base_state dict. Should be {type(component.__dict__[k])} but is {type(v)}."
                    )
                )
            return False

    # ensure type of config is valid
    if not isinstance(component.config(), dict):
        if warnings:
            print(
                term.red(f"Must return dictionary for config method for {component}.")
            )
        return False

    for k, v in component.config().items():

        # check that the attributes match
        if not hasattr(component, k):
            if warnings:
                print(
                    term.red(
                        f"Invalid attribute {k} for {component}. Valid attributes are {component.__dict__}"
                    )
                )
            return False

        # check that the configuration tuple is valid
        if type(v) not in [tuple, list] or len(v) != 2 or not isinstance(v[0], type):
            if warnings:
                print(
                    term.red(
                        f"Invalid configuration for {k} in {component}. Should be (type, default)."
                    )
                )
            return False

    if isinstance(component, Sensor):
        if not callable(getattr(component, "read", None)):
            if warnings:
                print(
                    term.red(
                        "Sensors must have a read method that returns the sensor's data"
                    )
                )
            return False

        try:
            component.read()
        except NotImplementedError:
            if warnings:
                print(
                    term.red(
                        "Sensors must have a read method that returns the sensor's data"
                    )
                )
            return False
        except BaseException:
            pass

    return True
