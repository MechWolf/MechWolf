"""Data management functions for reagent entry."""
import json
from typing import Dict, Any

class ReagentDataManager:
    """Manages reagent data loading, saving, and validation."""
    
    def __init__(self, data_file: str):
        """
        Initialize with data file path.
        
        Parameters:
        -----------
        data_file : str
            Path to the JSON file containing reagent data
        """
        self.data_file = data_file
        self.data = {"solid reagents": [], "liquid reagents": []}
        self.load_data()
        
    def load_data(self) -> Dict[str, Any]:
        """
        Load reagent data from JSON file.
        
        Returns:
        --------
        dict
            The loaded data
        """
        try:
            with open(self.data_file, "r") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {"solid reagents": [], "liquid reagents": []}
        return self.data

    def save_data(self) -> None:
        """Save reagent data to JSON file."""
        try:
            # Ensure critical keys exist
            if "solid reagents" not in self.data:
                self.data["solid reagents"] = []
            if "liquid reagents" not in self.data:
                self.data["liquid reagents"] = []
                
            with open(self.data_file, "w") as f:
                json.dump(self.data, f, indent=4)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            
    def add_reagent(self, reagent: Dict[str, Any], reagent_type: str) -> None:
        """
        Add a reagent to the data.
        
        Parameters:
        -----------
        reagent : dict
            Dictionary containing reagent data
        reagent_type : str
            Type of reagent ('solid' or 'liquid')
        """
        key = f"{reagent_type} reagents"
        
        # Make sure these categories exist in data
        if "solid reagents" not in self.data:
            self.data["solid reagents"] = []
        if "liquid reagents" not in self.data:
            self.data["liquid reagents"] = []
            
        # Make sure the key exists
        if key not in self.data:
            self.data[key] = []

        # Check if reagent with same name already exists
        for i, existing in enumerate(self.data[key]):
            if existing.get('name') == reagent.get('name'):
                # Update instead of add
                self.data[key][i] = reagent
                self.save_data()
                return
                
        # If not found, add as new
        self.data[key].append(reagent)
        self.save_data()
        
    def update_reagent(self, old_reagent: Dict[str, Any], new_reagent: Dict[str, Any], reagent_type: str) -> None:
        """
        Update an existing reagent in the data.
        
        Parameters:
        -----------
        old_reagent : dict
            Original reagent data to replace
        new_reagent : dict
            New reagent data
        reagent_type : str
            Type of reagent ('solid' or 'liquid')
        """
        key = f"{reagent_type} reagents"
        # Make sure the key exists in data
        if key not in self.data:
            self.data[key] = []
            
        # Find the reagent by name instead of direct object comparison
        found = False
        
        for i, reagent in enumerate(self.data[key]):
            if reagent.get('name') == old_reagent.get('name'):
                self.data[key][i] = new_reagent
                found = True
                break
                
        if not found:
            # Either it wasn't found or this is a new reagent
            self.data[key].append(new_reagent)
            
        # Always save after updating
        self.save_data()
        
    def delete_reagent(self, reagent: Dict[str, Any]) -> None:
        """
        Remove a reagent from the data.
        
        Parameters:
        -----------
        reagent : dict
            Reagent data to remove
        """
        if reagent in self.data["solid reagents"]:
            self.data["solid reagents"].remove(reagent)
        elif reagent in self.data["liquid reagents"]:
            self.data["liquid reagents"].remove(reagent)
        self.save_data()
        
    def get_reagent_type(self, reagent: Dict[str, Any]) -> str:
        """
        Determine the type of a reagent.
        
        Parameters:
        -----------
        reagent : dict
            Reagent data
            
        Returns:
        --------
        str
            'solid' or 'liquid'
        """
        # Check by name first which is more reliable
        reagent_name = reagent.get('name', '')
        
        # Check solid reagents
        for solid in self.data["solid reagents"]:
            if solid.get('name') == reagent_name:
                return "solid"
                
        # Check liquid reagents
        for liquid in self.data["liquid reagents"]:
            if liquid.get('name') == reagent_name:
                return "liquid"
                
        # Fallback to direct comparison (less reliable)
        return "solid" if reagent in self.data["solid reagents"] else "liquid"
        
    def update_final_details(self, mass_scale: float, concentration: float, solvent: str) -> None:
        """
        Update the final details in the data.
        
        Parameters:
        -----------
        mass_scale : float
            Mass scale in mg
        concentration : float
            Concentration in mM
        solvent : str
            Solvent name(s)
        """
        self.data["mass scale (in mg)"] = mass_scale
        self.data["concentration (in mM)"] = concentration
        self.data["solvent"] = solvent
        self.save_data()
        
    def has_limiting_reagent(self) -> bool:
        """
        Check if at least one reagent has an equivalent of 1.0.
        
        Returns:
        --------
        bool
            True if a limiting reagent exists, False otherwise
        """
        return any(
            abs(reagent["eq"] - 1.0) < 1e-6
            for reagent in self.data["solid reagents"] + self.data["liquid reagents"]
        )
