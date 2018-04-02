from .component import Component
from cirpy import Molecule
from terminaltables import SingleTable
import re

class Vessel(Component):
    def __init__(self, description, name=None, resolve=True, warnings=False):
        if resolve:
            hits = list(re.findall(r"`(.+?)`", description))
            try: # in case the resolver is down, don't break
                for hit in hits:
                    M = Molecule(hit)
                    description = description.replace(f"`{hit}`", f"{hit} ({M.iupac_name})" if hit.lower() != M.iupac_name.lower() else hit)

                    if warnings:
                        table = SingleTable([
                            ["IUPAC Name", M.iupac_name],
                            ["CAS", M.cas],
                            ["Formula", M.formula]])
                        table.title = "Resolved: " + hit
                        table.inner_heading_row_border = False
                        print(table.table)
            except:
                warn(Fore.YELLOW + "Resolver failed. Continuing without resolving.")

        super().__init__(name=description)

        self.description = description
