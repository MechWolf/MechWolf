import json
from typing import Any, Dict, Optional


class ProtocolDataManager:
    """
    Manages protocol data stored in a JSON file.
    Attributes:
        json_file (str): Path to the JSON file containing protocol data.
    Methods:
        load_full_config() -> Optional[Dict[str, Any]]:
            Loads the entire configuration file.
        load_protocol_config() -> Optional[Dict[str, Any]]:
            Loads the existing protocol configuration from the JSON file.
        save_protocol_config(protocol_config: Dict[str, Any]) -> None:
            Saves the protocol configuration while preserving all existing data.
    """

    def __init__(self, json_file: str) -> None:
        self.json_file = json_file

    def load_full_config(self) -> Optional[Dict[str, Any]]:
        """Load the entire configuration file"""
        try:
            with open(self.json_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading full configuration: {str(e)}")
            return None

    def load_protocol_config(self) -> Optional[Dict[str, Any]]:
        """Load existing protocol configuration from JSON file"""
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "protocol_configs" in data:
                    if data["protocol_configs"]:
                        return data["protocol_configs"][-1]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None

    def save_protocol_config(self, protocol_config: Dict[str, Any]) -> None:
        """Save protocol configuration while preserving ALL existing data"""
        try:
            # Read existing data
            with open(self.json_file, "r") as f:
                data = json.load(f)
            print(f"Successfully read existing data from {self.json_file}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Creating new data file due to: {str(e)}")
            data = {}

        # Create new protocol entry
        new_entry = {
            "name": protocol_config.get(
                "name", ""
            ),  # Default to empty string if not provided
            "description": protocol_config.get(
                "description", ""
            ),  # Default to empty string if not provided
            "pump_entries": protocol_config["pump_entries"],
        }

        # Ensure protocol_configs exists
        if "protocol_configs" not in data:
            data["protocol_configs"] = []
            print("Created new protocol_configs section")

        # Update or append protocol
        found = False
        for i, existing_protocol in enumerate(data["protocol_configs"]):
            if existing_protocol.get("name") == new_entry["name"]:
                data["protocol_configs"][i] = new_entry
                found = True
                print(f"Updated existing protocol: {new_entry['name']}")
                break

        if not found:
            data["protocol_configs"].append(new_entry)
            print(f"Added new protocol: {new_entry['name']}")

        # Write back to file with proper formatting
        try:
            with open(self.json_file, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Successfully wrote data to {self.json_file}")
            print(
                f"Protocol '{new_entry['name']}' saved with {len(new_entry['pump_entries'])} entries"
            )
        except Exception as e:
            print(f"Error writing to file: {str(e)}")
            raise
