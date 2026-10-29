import json

"""
Processes reagent data from a JSON file and generates a stoichiometry table.
Args:
    data_file (str): Path to the JSON file containing reagent data.
Raises:
    AssertionError: If any required field is missing in the reagent data.
Classes:
    Reagent: Represents a chemical reagent with attributes such as name, inChi, inChiKey, SMILES, molecular weight, eq, syringe, moles, and mass.
    Solid: Inherits from Reagent and represents a solid reagent.
    Liquid: Inherits from Reagent and represents a liquid reagent with additional attributes for density and volume.
Functions:
    process_data(data_file: str) -> None: Processes the reagent data, calculates moles and mass, and generates a stoichiometry table.
    main() -> None: Placeholder function for script entry point.
Example:
    To use this script, call the `process_data` function with the path to the JSON file containing reagent data:
    process_data("path/to/data_file.json")
"""
from astropy.table import QTable
from sigfig import round
from typing import Dict, Any, Optional, List


class Reagent:
    def __init__(self, reagent: Dict[str, Any], moles: float) -> None:
        assert (
            "name" in reagent
        ), "ERROR: one of the reagents does not have a name field"
        assert (
            "inChi" in reagent
        ), f'Error: {reagent["name"]} does not have an inChi field'
        assert (
            "inChi Key" in reagent
        ), f'Error: {reagent["name"]} does not have an inChi key field'
        assert (
            "molecular weight (in g/mol)" in reagent
        ), f'Error: {reagent["name"]} does not have a molecular weight field'
        assert "eq" in reagent, f'Error: {reagent["name"]} does not have an eq field'
        assert (
            "syringe" in reagent
        ), f'Error: {reagent["name"]} does not have a syringe # field'

        self.name: str = reagent["name"]
        self.inChi: str = reagent["inChi"]
        self.inChiKey: str = reagent["inChi Key"]
        self.SMILES: str = reagent["SMILES"]
        self.mol_weight: float = reagent["molecular weight (in g/mol)"]
        self.eq: float = reagent["eq"]
        self.syringe: int = reagent["syringe"]
        self.moles: float = round(moles * self.eq, decimals=4)
        self.mass: float = round(self.moles * self.mol_weight, decimals=4)

    def __str__(self) -> str:
        return f"{self.name}"

    def get_name_and_eq(self) -> str:
        return f"{self.name}: {self.eq}"


class Solid(Reagent):
    def __init__(self, reagent: Dict[str, Any], moles: float) -> None:
        super().__init__(reagent, moles)


class Liquid(Reagent):
    def __init__(self, reagent: Dict[str, Any], moles: float) -> None:
        super().__init__(reagent, moles)
        assert (
            "density (in g/mL)" in reagent
        ), f'Error: {reagent["name"]} does not have a density field'
        self.density: float = reagent["density (in g/mL)"]
        self.volume: float = round(
            self.eq * moles * (self.mol_weight / self.density), decimals=4
        )


def process_data(data_file: str) -> None:
    with open(data_file, "r") as f:
        data: Dict[str, Any] = json.load(f)

    limiting_reagent: Optional[str] = None
    mw_limiting: Optional[float] = None

    for reagent in data["solid reagents"] + data["liquid reagents"]:
        if reagent["eq"] == 1:
            limiting_reagent = reagent["name"]
            mw_limiting = reagent["molecular weight (in g/mol)"]
            break

    if mw_limiting is not None:
        mass_scale: float = data["mass scale (in mg)"]
        moles_limiting: float = mass_scale / mw_limiting

        solid_reagents: List[Solid] = [
            Solid(reagent, moles_limiting) for reagent in data["solid reagents"]
        ]
        liquid_reagents: List[Liquid] = [
            Liquid(reagent, moles_limiting) for reagent in data["liquid reagents"]
        ]

        # Print data with just the name of reagent and their InChi, InChi key, and SMILES
        print("Reagent Data:")
        for reagent in solid_reagents + liquid_reagents:
            print(
                f"{reagent.name}: InChi: {reagent.inChi} | InChi Key: {reagent.inChiKey} | SMILES: {reagent.SMILES}\n"
            )

        # Print the name of the limiting reagent and its moles
        print(f"\nLimiting Reagent: {limiting_reagent} | Moles: {moles_limiting:.4f}\n")

        # Print the list of solvents
        print(f"Solvents: {data['solvent']}\n")

        # Generate stoichiometry table
        reagent_list: List[Reagent] = solid_reagents + liquid_reagents

        reagent_table: QTable = QTable()
        reagent_table["Reagent"] = [reagent.name for reagent in reagent_list]
        reagent_table["Molecular Weight (g/mol)"] = [
            reagent.mol_weight for reagent in reagent_list
        ]
        reagent_table["Amount (mmol)"] = [
            round(reagent.moles, decimals=4) for reagent in reagent_list
        ]
        reagent_table["Mass (mg)"] = [
            round(reagent.mass, decimals=4) for reagent in reagent_list
        ]
        reagent_table["Volume (mL)"] = [
            round((reagent.volume / 1000), decimals=4)
            if hasattr(reagent, "volume") and reagent.volume != 0
            else "N/A"
            for reagent in reagent_list
        ]
        reagent_table["Density (g/mL)"] = [
            reagent.density if hasattr(reagent, "density") else "N/A"
            for reagent in reagent_list
        ]
        reagent_table["eq"] = [reagent.eq for reagent in reagent_list]
        reagent_table["Syringe"] = [reagent.syringe for reagent in reagent_list]
        reagent_table["Concentration (M, mol/L)"] = [
            round(data["concentration (in mM)"] * reagent.eq / 1000, decimals=3)
            for reagent in reagent_list
        ]

        reagent_table.pprint(max_lines=-1, max_width=-1)

        # Calculate volume of solution in the syringes
        if data["concentration (in mM)"] != 0:
            volume_solution: float = moles_limiting / (
                data["concentration (in mM)"] / 1000
            )
            print(f"Volume of solution in the syringes: {volume_solution:.4f} mL")
        else:
            print("Error: Concentration cannot be zero.")


def main() -> None:
    # This function is no longer needed
    pass


if __name__ == "__main__":
    main()
