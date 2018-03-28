from warnings import warn
from abc import ABCMeta, abstractmethod
from colorama import Fore


class Component(object):
    """One of the individial, irreducible parts of a flow chemistry setup.

    All components in an :class:`flow.Apparatus` must be of type
    :class:`Component`. However, it is unlikely that a user will directly
    instantiate a :class:`Component`.

    Attributes:
        name (str, optional): the name of the component.
    """
    _id_counter = 0
    used_names = set()

    def __init__(self, name=None):
        # name the object, either sequentially or with a given name
        if name is None:
            self.name = self.__class__.__name__ + "_" + str(self.__class__._id_counter)
            self.__class__._id_counter += 1
        elif name not in self.__class__.used_names:
            self.name = name
        else:
            raise ValueError(Fore.RED + f"Cannot have two components with the name {name}.")
        self.__class__.used_names.add(self.name)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

class ActiveComponent(Component, metaclass=ABCMeta):
    """A connected, controllable component.

    All components beind manipulated in an :class:`flow.Protocol` must be of
    type :class:`ActiveComponent`.

    Warning:
        Users should not directly instantiate an :class:`ActiveComponent`
        because it is an abstract base class, not a functioning laboratory
        instrument.

     Attributes:
        Name (str, optional): the name of the component.

    """
    _id_counter = 0

    def __init__(self, name=None):
        if name is None:
            raise ValueError(Fore.RED + "No name given for ActiveComponent. Specify the name of the component by adding name=\"[name of component]\" to the line that generated this error.")
        super().__init__(name=name)

    def update_from_params(self, params):
        '''Updates the attributes of the object from a dict.

        Args:
            params (dict): A dict whose keys are the strings of attribute names
            and values are the new values of the attribute.

        '''
        for key, value in params.items():
            setattr(self, key, value)

    @abstractmethod
    def base_state():
        '''A placeholder method for the base state of the component.

        All subclasses of ActiveComponent must implement a function that returns
        a dict of its base state. At the end of a protocol, the component will
        return to this state.

        Note:
            The dict that :meth:`ActiveComponent.base_state` returns, must have values which
            can be parsed into compatible units of the object's attributes, if applicable.
            For example, :meth:`Pump.base_state` returns ``{"rate": "0 ml/min"}``.
        '''
        pass
