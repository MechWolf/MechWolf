from .components import ActiveComponent
from . import ureg
from colorama import Fore

def validate_component(component):
    '''Checks if a component's class is valid.

    Arguments:
        component (Component): The component being validated.

    Returns:
        bool: True if valid, else False.
    '''
    # ensure is an ActiveComponent
    if not issubclass(component.__class__, ActiveComponent):
        print(Fore.RED + f"{component} is not an instance of ActiveComponent")
        return False

    # must have an update method
    elif not callable(getattr(component, "update", None)):
        print(Fore.RED + f"{component} does not have an update method")
        return False

    # must have a base_state method
    elif not callable(getattr(component, "base_state", None)):
        print(Fore.RED + f"{component} does not have a base_state method")
        return False

    # base_state method must return a dict
    elif type(component.base_state()) != dict:
        print(Fore.RED + "base_state method does not return a dict")
        return False

    # the base_state dict must not be empty
    elif not component.base_state():
        print(Fore.RED + "base_state method dict must not be empty")
        return False

    # validate the base_state dict
    for k, v in component.base_state().items():
        if not hasattr(component, k):
            print(Fore.RED + f"Invalid attribute {k} for {component}. Valid attributes are {component.__dict__}")
            return False
        if type(component.__dict__[k]) == ureg.Quantity and ureg.parse_expression(v).dimensionality != component.__dict__[k].dimensionality:
            print(Fore.RED + f"Invalid dimensionality {ureg.parse_expression(v).dimensionality} for {k} for {component}.")
            return False
        elif type(component.__dict__[k]) != ureg.Quantity and type(component.__dict__[k]) != type(v):
            print(Fore.RED + f"Bad type matching for {k} in base_state dict. Should be {type(component.__dict__[k])} but is {type(v)}.")

    return True
