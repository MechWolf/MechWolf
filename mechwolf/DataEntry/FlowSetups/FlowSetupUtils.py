import re
from typing import Optional, List, Dict, Any

"""
Utility functions for handling dimension conversions, tube parsing, and field validation.

Functions:
    convert_dimension_to_float(dimension):
        Convert a dimension string to float value in inches.
            dimension (str): The dimension string to convert.
            float: The dimension in inches, or None if conversion fails.
    parse_tube_dimension(value):
        Parse tube dimension that could be fraction or decimal.
            value (str): The tube dimension string to parse.
            str: The parsed tube dimension in inches, or None if parsing fails.
    parse_numeric_foot(value):
        Parse numeric values to foot units.
            value (str): The numeric value string to parse.
            str: The parsed value in foot units, or None if parsing fails.
    validate_required_fields(data, use_rmv=False):
        Validate all required fields are present.
            data (dict): Dictionary containing field values.
            use_rmv (bool, optional): Toggle between Product Vessel and Reaction Mixture Vessel validation. Defaults to False.
            list: List of missing field names.
    check_required_fields(data):
        Alias for validate_required_fields with default settings.
            data (dict): Dictionary containing field values.
            list: List of missing field names.
    validate_required_fields_with_rmv(data):
        Alias for validate_required_fields with RMV enabled.
            data (dict): Dictionary containing field values.
            list: List of missing field names.
    get_coil_letter(index):
        Convert numeric index to coil letter sequence.
            index (int): The numeric index to convert.
            str: The corresponding coil letter, or None if index is out of range.
    get_coil_index(letter):
        Convert coil letter to numeric index.
            letter (str): The coil letter to convert.
            int: The corresponding numeric index, or None if letter is invalid.
"""


def convert_dimension_to_float(dimension: str) -> Optional[float]:
    """Convert a dimension string to float value in inches"""
    try:
        # Handle fraction format
        fraction_match = re.match(r"(\d+)/(\d+)\s*(?:in)?", str(dimension))
        if fraction_match:
            num, denom = map(int, fraction_match.groups())
            return num / denom

        # Handle decimal format
        number = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(dimension))[0])
        return number
    except (IndexError, ValueError, TypeError, ZeroDivisionError):
        return None


def parse_tube_dimension(value: str) -> Optional[str]:
    """Parse tube dimension that could be fraction or decimal"""
    try:
        fraction_match = re.match(r"(\d+)/(\d+)\s*(?:in)?", value)
        if fraction_match:
            num, denom = map(int, fraction_match.groups())
            return f"{num}/{denom} in"

        number = float(re.findall(r"[-+]?\d*\.\d+|\d+", value)[0])
        return f"{number} in"
    except (IndexError, ValueError):
        return None


def parse_numeric_foot(value: str) -> Optional[str]:
    """Parse numeric values to foot units"""
    try:
        number = float(re.findall(r"[-+]?\d*\.\d+|\d+", value)[0])
        return f"{number} foot"
    except (IndexError, ValueError):
        return None


def validate_required_fields(data: Dict[str, Any], use_rmv: bool = False) -> List[str]:
    """Validate all required fields are present
    Args:
        data: Dictionary containing field values
        use_rmv: Boolean to toggle between Product Vessel and Reaction Mixture Vessel validation
    Returns:
        List of missing field names
    """
    vessel_field_name = (
        "Reaction Mixture Vessel Name" if use_rmv else "Product Vessel Name"
    )
    vessel_key = "reaction_mixture_vessel_name" if use_rmv else "product_vessel_name"

    required_fields = {
        "Apparatus Name": data.get("apparatus_name"),
        "Vessel 1 Name": data.get("vessel1_name"),
        "Vessel 2 Name": data.get("vessel2_name"),
        vessel_field_name: data.get(vessel_key),
        "Reaction Tube ID": data.get("reaction_tube_id_raw"),
        "Reaction Tube OD": data.get("reaction_tube_od_raw"),
        "Reaction Tube Material": data.get("reaction_tube_material"),
        "Coil A Length": data.get("coil_a_raw"),
        "Coil X Length": data.get("coil_x_raw"),
    }
    return [name for name, value in required_fields.items() if not value]


# Maintain backward compatibility
def check_required_fields(data: Dict[str, Any]) -> List[str]:
    """Alias for validate_required_fields with default settings"""
    return validate_required_fields(data, use_rmv=False)


# Keep the old name for backward compatibility but make it use the new function
def validate_required_fields_with_rmv(data: Dict[str, Any]) -> List[str]:
    """Alias for validate_required_fields with RMV enabled"""
    return validate_required_fields(data, use_rmv=True)


def get_coil_letter(index: int) -> Optional[str]:
    """Convert numeric index to coil letter sequence"""
    coil_letters = ["a", "x", "b", "y"]
    try:
        return coil_letters[index]
    except IndexError:
        return None


def get_coil_index(letter: str) -> Optional[int]:
    """Convert coil letter to numeric index"""
    coil_letters = ["a", "x", "b", "y"]
    try:
        return coil_letters.index(letter.lower())
    except ValueError:
        return None
