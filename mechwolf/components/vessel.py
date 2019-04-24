import logging
import re
from warnings import warn

from cirpy import Molecule
from terminaltables import SingleTable

from . import term
from .component import Component

# ignore annoying CIRpy warnings
logging.getLogger("cirpy").setLevel(logging.WARNING)

class Vessel(Component):
    """A generic vessel.

    Attributes:
        description (str): The contents of the Vessel.
        name (str): The name of the vessel, if different from the description.
        resolve (bool, optional): Whether to resolve the names of chemicals surrounded by :literal:`\`` s into their IUPAC names. Defaults to True.
        warnings (bool, optional): Whether to show the resolved chemicals for manual confirmation. Defaults to False.
    """ # noqa

    def __init__(self, description, resolve=True, warnings=False, name=None):

        # handle the resolver logic
        if resolve:
            # find the tagged chemical names
            hits = list(re.findall(r"`(.+?)`", description))

            for hit in hits:
                M = Molecule(hit)
                try: # in case the resolver is down, don't break
                    description = description.replace(f"`{hit}`", f"{hit} ({M.iupac_name})" if hit.lower() != M.iupac_name.lower() else hit)
                except BaseException:
                    warn(term.yellow(f"Failed to resolve {hit}. Continuing without resolving."))
                    continue
                # show a warning table
                if warnings:
                    table = SingleTable([
                        ["IUPAC Name", M.iupac_name],
                        ["CAS", M.cas],
                        ["Formula", M.formula]])
                    table.title = "Resolved: " + hit
                    table.inner_heading_row_border = False
                    print(table.table)
        super().__init__(name=name)
        self.description = description
        self._visualization_shape = "cylinder"
