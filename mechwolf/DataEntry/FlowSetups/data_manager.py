import json
from typing import Optional, Dict, Any


class DataManager:
    def __init__(self, json_file: str) -> None:
        """
        Initializes the DataManager with the given JSON file.

        Args:
            json_file (str): The path to the JSON file to be managed.
        """
        self.json_file: str = json_file

    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load existing apparatus configuration from JSON file"""
        try:
            with open(self.json_file, "r") as f:
                data: Dict[str, Any] = json.load(f)
                if isinstance(data, dict) and "apparatus_config" in data:
                    return data["apparatus_config"]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None

    def save_config(self, apparatus_config: Dict[str, Any]) -> None:
        """Save configuration while preserving other data"""
        try:
            # Try to read existing data
            with open(self.json_file, "r") as f:
                existing_data: Dict[str, Any] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}

        # Preserve all existing data except apparatus config
        existing_data["apparatus_config"] = apparatus_config

        # Ensure coils have both length and index if not already present
        if "coils" in apparatus_config:
            for coil in apparatus_config["coils"]:
                if "index" not in coil and "length" in coil:
                    # If index is missing but we have order, infer index
                    idx: int = apparatus_config["coils"].index(coil)
                    coil["index"] = ["a", "x", "b", "y"][idx]

        # Preserve specific reaction setup data if it exists
        reaction_fields = [
            "solid reagents",
            "liquid reagents",
            "mass scale (in mg)",
            "concentration (in mM)",
            "solvent",
        ]

        # Write back all data
        with open(self.json_file, "w") as f:
            json.dump(existing_data, f, indent=4)
