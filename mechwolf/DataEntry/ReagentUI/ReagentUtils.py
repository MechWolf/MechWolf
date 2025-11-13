"""Utility functions for MechWolf DataEntry module."""
import sys
import os
from contextlib import contextmanager

# Context manager to suppress stderr
@contextmanager
def suppress_stderr():
    old_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = old_stderr

def validate_smiles(smiles_string):
    """
    Validate a SMILES string with basic checks.
    
    Parameters:
    -----------
    smiles_string : str
        The SMILES string to validate
        
    Returns:
    --------
    bool
        True if the SMILES string passes basic validation, False otherwise
    """
    if not smiles_string or not isinstance(smiles_string, str):
        return False
    
    # Basic validation - must have letters and reasonable length
    if len(smiles_string) < 1 or not any(c.isalpha() for c in smiles_string):
        return False
    
    # Check for unmatched brackets/parentheses
    brackets = {'[': ']', '(': ')'}
    stack = []
    
    for char in smiles_string:
        if char in brackets.keys():
            stack.append(char)
        elif char in brackets.values():
            if not stack or char != brackets.get(stack.pop(), None):
                return False
    
    # Check for unclosed rings (numbers should appear in pairs)
    digits = [c for c in smiles_string if c.isdigit()]
    digit_counts = {}
    for d in digits:
        digit_counts[d] = digit_counts.get(d, 0) + 1
    
    # Each ring number should appear exactly twice
    for count in digit_counts.values():
        if count % 2 != 0:
            return False
    
    # Additional validation with RDKit if available
    try:
        from rdkit import Chem
        from rdkit import RDLogger
        # Disable RDKit logging
        RDLogger.DisableLog('rdApp')
        # Suppress stderr during SMILES parsing
        with suppress_stderr():
            mol = Chem.MolFromSmiles(smiles_string, sanitize=False)
            return mol is not None
    except ImportError:
        # RDKit not available, just return the bracket validation result
        pass
    
    return len(stack) == 0  # All brackets should be matched

def try_sanitize_smiles(smiles_string):
    """
    Attempts to sanitize a SMILES string by handling common errors.
    
    Parameters:
    -----------
    smiles_string : str
        The potentially invalid SMILES string
        
    Returns:
    --------
    str
        Sanitized SMILES string if possible, empty string if not salvageable
    """
    if not smiles_string or not isinstance(smiles_string, str):
        return ""
    
    # Remove any whitespace
    sanitized = smiles_string.strip()
    
    # Handle unclosed rings by removing the opening digit
    digits = [i for i, c in enumerate(sanitized) if c.isdigit()]
    digit_chars = [sanitized[i] for i in digits]
    
    # Find digits that appear only once
    from collections import Counter
    counts = Counter(digit_chars)
    single_digits = [d for d, count in counts.items() if count % 2 != 0]
    
    # Remove unclosed rings (risky but better than failing)
    for digit in single_digits:
        indices = [i for i, c in enumerate(sanitized) if c == digit]
        # Remove the first occurrence of each problematic digit
        if indices:
            sanitized = sanitized[:indices[0]] + sanitized[indices[0]+1:]
    
    return sanitized if validate_smiles(sanitized) else ""

# Add new utility functions for RDKit operations
def safe_mol_from_smiles(smiles):
    """
    Create a molecule from SMILES with error suppression.
    
    Parameters:
    -----------
    smiles : str
        The SMILES string to convert
        
    Returns:
    --------
    RDKit.Chem.Mol or None
        Molecule object if successful, None otherwise
    """
    try:
        from rdkit import Chem
        from rdkit import RDLogger
        # Disable RDKit logging
        RDLogger.DisableLog('rdApp')
        
        with suppress_stderr():
            mol = Chem.MolFromSmiles(smiles, sanitize=False)
            if mol is not None:
                try:
                    Chem.SanitizeMol(mol)
                except:
                    pass
            return mol
    except ImportError:
        return None
    except:
        return None

def is_rdkit_available():
    """
    Check if RDKit is available in the environment.
    
    Returns:
    --------
    bool
        True if RDKit is available, False otherwise
    """
    try:
        import rdkit
        return True
    except ImportError:
        return False

def validate_reagent_data(data, reagent_type):
    """
    Validate reagent data and return a dictionary of errors.
    
    Parameters:
    -----------
    data : dict
        Dictionary containing reagent data
    reagent_type : str
        Type of reagent ('solid' or 'liquid')
        
    Returns:
    --------
    dict
        Dictionary of validation errors, empty if valid
    """
    errors = {}
    
    # Name validation
    if not data.get("name") or data["name"].strip() == "":
        errors["name"] = "Name is required"
    
    # Equivalents validation
    if data.get("eq", 0) <= 0:
        errors["eq"] = "Equivalents must be greater than 0"
        
    # Molecular weight validation
    if data.get("molecular weight (in g/mol)", 0) <= 0:
        errors["mw"] = "Molecular weight must be greater than 0"
    
    # Density validation for liquids
    if reagent_type == "liquid" and data.get("density (in g/mL)", 0) <= 0:
        errors["density"] = "Density must be greater than 0"
    
    # Syringe validation - must be an integer > 0
    if data.get("syringe", 0) <= 0:
        errors["syringe"] = "Syringe must be greater than 0"
    
    return errors
