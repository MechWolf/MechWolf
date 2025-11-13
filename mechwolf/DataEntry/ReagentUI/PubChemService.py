"""PubChem API service for chemical data retrieval."""
import requests
from typing import Dict, Any, List, Optional
from mechwolf.DataEntry.ReagentUI.ReagentUtils import validate_smiles, suppress_stderr, safe_mol_from_smiles

class PubChemService:
    """Service for interacting with the PubChem API."""
    
    def __init__(self):
        """Initialize the service with an empty cache."""
        self.cache = {}
        
    def search(self, query: str, search_type: str) -> List[Dict[str, Any]]:
        """
        Search PubChem database and return results.
        
        Parameters:
        -----------
        query : str
            Search query
        search_type : str
            Type of search ('name', 'smiles', 'inchi', 'inchi key', 'cas')
            
        Returns:
        --------
        list
            List of compound dictionaries with chemical data
        """
        base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        
        # Check if result is in cache
        cache_key = f"{search_type}:{query}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Validate input before sending to PubChem
            if search_type == 'smiles' and not validate_smiles(query):
                return []
            
            # Map search type to PubChem's input types
            input_type = {
                'name': 'name',
                'smiles': 'smiles',
                'inchi': 'inchi',
                'inchi key': 'inchikey',
                'cas': 'cas'  # Change this to a simple identifier
            }.get(search_type, 'name')
            
            # Different endpoint based on search type
            if input_type == 'cas':
                # Special handling for CAS Registry Numbers
                url = f"{base_url}/compound/xref/RN/{query}/cids/JSON"
            else:
                url = f"{base_url}/compound/{input_type}/{query}/cids/JSON"
            
            # Get compound IDs with timeout and error handling
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'IdentifierList' not in data:
                return []
                
            cids = data['IdentifierList']['CID'][:5]  # Limit to first 5 results
            
            # Get compound data for each CID
            results = []
            for cid in cids:
                # Get properties
                prop_url = f"{base_url}/compound/cid/{cid}/property/IUPACName,MolecularFormula,MolecularWeight,InChI,InChIKey,CanonicalSMILES/JSON"
                prop_response = requests.get(prop_url, timeout=10)
                prop_response.raise_for_status()
                
                props = prop_response.json()['PropertyTable']['Properties'][0]
                
                # Validate SMILES before including in result
                smiles = props.get('CanonicalSMILES', '')
                
                # Use safe mol creation that doesn't print errors
                with suppress_stderr():
                    if not safe_mol_from_smiles(smiles):
                        smiles = ''  # Invalid SMILES, clear it
                
                # Create result object
                compound = {
                    'cid': cid,
                    'name': props.get('IUPACName', ''),
                    'formula': props.get('MolecularFormula', ''),
                    'molecular_weight': float(props.get('MolecularWeight', 0)),
                    'inchi': props.get('InChI', ''),
                    'inchikey': props.get('InChIKey', ''),
                    'smiles': smiles,
                    'density': self.get_density(cid)  # Get density for the compound
                }
                
                results.append(compound)
            
            # Cache results
            self.cache[cache_key] = results
            return results
            
        except requests.exceptions.Timeout:
            return []
        except requests.exceptions.RequestException as e:
            return []
        except Exception as e:
            return []
            
    def get_density(self, cid: str) -> Optional[float]:
        """
        Retrieve the density for a compound from PubChem.
        
        Parameters:
        -----------
        cid : str
            PubChem Compound ID
            
        Returns:
        --------
        float or None
            Density in g/mL if available, None otherwise
        """
        try:
            # Get all physical properties instead of filtering by density heading
            base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view"
            url = f"{base_url}/data/compound/{cid}/JSON"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Navigate through the JSON to find density
            if 'Record' in data and 'Section' in data['Record']:
                for section in data['Record']['Section']:
                    if 'TOCHeading' in section and section['TOCHeading'] == 'Chemical and Physical Properties':
                        if 'Section' in section:
                            for subsection in section['Section']:
                                if 'TOCHeading' in subsection and subsection['TOCHeading'] == 'Experimental Properties':
                                    if 'Section' in subsection:
                                        for prop_section in subsection['Section']:
                                            if 'TOCHeading' in prop_section and prop_section['TOCHeading'] == 'Density':
                                                if 'Information' in prop_section:
                                                    for info in prop_section['Information']:
                                                        # Try to extract density from various formats
                                                        if 'Value' in info:
                                                            # Check for direct number value
                                                            if 'Number' in info['Value']:
                                                                try:
                                                                    density_value = float(info['Value']['Number'][0])
                                                                    return density_value
                                                                except (ValueError, IndexError):
                                                                    pass
                                                            
                                                            # Check for string with markup (e.g., "0.867 at 68 °F")
                                                            if 'StringWithMarkup' in info['Value']:
                                                                for value_item in info['Value']['StringWithMarkup']:
                                                                    if 'String' in value_item:
                                                                        string_val = value_item['String']
                                                                        # Extract numeric part using regex
                                                                        import re
                                                                        # Look for patterns like "0.867" or "0.8623 g/cu cm"
                                                                        match = re.search(r'([0-9]*\.?[0-9]+)', string_val)
                                                                        if match:
                                                                            try:
                                                                                return float(match.group(1))
                                                                            except ValueError:
                                                                                pass
            
            # If no density found in experimental properties, try computed properties
            if 'Record' in data and 'Section' in data['Record']:
                for section in data['Record']['Section']:
                    if 'TOCHeading' in section and section['TOCHeading'] == 'Chemical and Physical Properties':
                        if 'Section' in section:
                            for subsection in section['Section']:
                                if 'TOCHeading' in subsection and subsection['TOCHeading'] == 'Computed Properties':
                                    if 'Section' in subsection:
                                        for prop_section in subsection['Section']:
                                            if 'Information' in prop_section:
                                                for info in prop_section['Information']:
                                                    # Look for density information by matching the name
                                                    if 'Name' in info and 'density' in info['Name'].lower():
                                                        if 'Value' in info and 'StringWithMarkup' in info['Value']:
                                                            for value_item in info['Value']['StringWithMarkup']:
                                                                if 'String' in value_item:
                                                                    string_val = value_item['String']
                                                                    # Extract numeric part using regex
                                                                    import re
                                                                    match = re.search(r'([0-9]*\.?[0-9]+)', string_val)
                                                                    if match:
                                                                        try:
                                                                            return float(match.group(1))
                                                                        except ValueError:
                                                                            pass
            
            # If no density found, return None
            return None
            
        except Exception as e:
            return None
