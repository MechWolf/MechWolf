import ipywidgets as widgets
from IPython.display import display, clear_output

# Import helper modules
from mechwolf.DataEntry.ReagentUI.DataManager import ReagentDataManager
from mechwolf.DataEntry.ReagentUI.PubChemService import PubChemService
from mechwolf.DataEntry.ReagentUI.UIComponents import UIComponents
from mechwolf.DataEntry.ReagentUI.FormHandlers import ReagentFormHandler, FinalDetailsFormHandler

class ReagentInputForm:
    def __init__(self, data_file: str) -> None:
        """Initialize the form with a data file path."""
        # Initialize data manager
        self.data_manager = ReagentDataManager(data_file)
        self.data_file = data_file
        
        # Initialize PubChem service
        self.pubchem_service = PubChemService()
        
        # Main UI components
        self.main_container = None
        self.tab_container = None
        self.add_reagents_tab = None
        self.current_reagents_tab = None
        self.final_details_tab = None
        self.search_tab = None
        
        # Search components
        self.search_input = None
        self.search_results = None
        self.search_status = None
        
        # List display
        self.reagent_list = None

    def setup_ui(self) -> None:
        """Create the main UI structure with tabs."""
        # Create the tab container
        self.tab_container = widgets.Tab()
        
        # Create tabs
        self.add_reagents_tab = self.create_add_reagents_tab()
        self.current_reagents_tab = self.create_current_reagents_tab()
        self.final_details_tab = self.create_final_details_tab()
        self.search_tab = self.create_search_tab()
        
        # Set the tab children and titles
        self.tab_container.children = [
            self.add_reagents_tab,
            self.current_reagents_tab,
            self.search_tab,
            self.final_details_tab
        ]
        self.tab_container.set_title(0, "Add Reagents")
        self.tab_container.set_title(1, "Current Reagents")
        self.tab_container.set_title(2, "Search Chemical")
        self.tab_container.set_title(3, "Final Details")
        
        # Add tab selection handler to refresh the final details tab when selected
        def on_tab_selected(change):
            if change['new'] == 3:  # Final Details tab index
                self.refresh_final_details_tab()
                
        self.tab_container.observe(on_tab_selected, names='selected_index')
        
        # Main container with tabs
        self.main_container = widgets.VBox([
            widgets.HTML("<h3>Reagent Entry Form</h3>"),
            self.tab_container
        ])
        
        # Display the main container
        display(self.main_container)
        
        # Update the reagent list
        self.update_reagent_list()

    def create_add_reagents_tab(self) -> widgets.Widget:
        """Create the tab content for adding reagents."""
        # Create an accordion for organizing solid and liquid forms
        reagent_accordion = widgets.Accordion()
        
        # Create solid reagent form
        solid_form = ReagentFormHandler.create_reagent_form(
            "solid", 
            on_save=self.save_reagent
        )
        
        # Create liquid reagent form
        liquid_form = ReagentFormHandler.create_reagent_form(
            "liquid", 
            on_save=self.save_reagent
        )
        
        # Set accordion children and titles
        reagent_accordion.children = [solid_form, liquid_form]
        reagent_accordion.set_title(0, "Solid Reagent")
        reagent_accordion.set_title(1, "Liquid Reagent")
        
        # Return the complete tab content
        return widgets.VBox([
            widgets.HTML("<h4>Add New Reagents</h4>"),
            reagent_accordion
        ], layout=widgets.Layout(padding="10px"))

    def create_current_reagents_tab(self) -> widgets.Widget:
        """Create the tab content for viewing current reagents."""
        # Create reagent list container
        self.reagent_list = widgets.VBox(
            layout=widgets.Layout(
                margin="10px 0 10px 0",
                border="1px solid #ddd",
                padding="10px",
                min_height="100px"
            )
        )
        
        # Return the complete tab content
        return widgets.VBox([
            widgets.HTML("<h4>Current Reagents</h4>"),
            self.reagent_list
        ], layout=widgets.Layout(padding="10px"))
    
    def create_final_details_tab(self) -> widgets.Widget:
        """Create the tab content for entering final details."""
        # Create the final details form
        form = FinalDetailsFormHandler.create_final_details_form(
            self.data_manager.data,
            on_submit=self.process_final_details
        )
        
        # Return the complete tab content
        return widgets.VBox([
            widgets.HTML("<h4>Final Details and Submission</h4>"),
            form
        ], layout=widgets.Layout(padding="10px"))

    def create_search_tab(self) -> widgets.Widget:
        """Create the tab content for searching chemicals from PubChem."""
        # Create search input area
        self.search_input = widgets.Text(
            placeholder="Enter chemical name, SMILES, InChI, or CAS",
            description="Search:",
            layout=widgets.Layout(width="80%")
        )
        
        search_type = widgets.Dropdown(
            options=['Name', 'SMILES', 'InChI', 'InChI Key', 'CAS'],
            value='Name',
            description='Search by:',
            layout=widgets.Layout(width="50%")
        )
        
        search_button = widgets.Button(
            description="Search PubChem",
            button_style="info",
            icon="search"
        )
        
        # Create status area
        self.search_status = widgets.HTML("")
        
        # Create results area
        self.search_results = widgets.VBox([])
        
        # Set up search button callback
        def on_search_click(b):
            query = self.search_input.value.strip()
            if not query:
                self.search_status.value = "<p style='color: orange;'>Please enter a search term</p>"
                return
                
            self.search_status.value = "<p style='color: blue;'>Searching PubChem...</p>"
            self.search_results.children = ()
            
            # Perform the search
            results = self.pubchem_service.search(query, search_type.value.lower())
            
            if not results:
                self.search_status.value = "<p style='color: red;'>No results found</p>"
                return
                
            self.search_status.value = f"<p style='color: green;'>Found {len(results)} results</p>"
            
            # Create result widgets
            result_widgets = []
            for compound in results:
                # Create a copy of the compound data for each result to avoid reference issues
                compound_copy = compound.copy()
                result_widget = UIComponents.create_search_result_widget(
                    compound_copy,
                    on_import_solid=self.import_from_pubchem_solid,
                    on_import_liquid=self.import_from_pubchem_liquid
                )
                result_widgets.append(result_widget)
                
            self.search_results.children = tuple(result_widgets)
            
        search_button.on_click(on_search_click)
        
        # Input area arrangement
        input_area = widgets.VBox([
            widgets.HBox([self.search_input, search_type]), 
            search_button,
            self.search_status
        ], layout=widgets.Layout(margin="10px 0"))
        
        # Results area with scrolling
        results_container = widgets.VBox([
            widgets.HTML("<h4>Search Results</h4>"),
            self.search_results
        ], layout=widgets.Layout(
            border="1px solid #ddd",
            padding="10px",
            margin="10px 0",
            max_height="500px",
            overflow_y="auto"
        ))
        
        # Return the complete tab content
        return widgets.VBox([
            widgets.HTML("<h4>Search Chemical Databases</h4>"),
            input_area,
            results_container
        ], layout=widgets.Layout(padding="10px"))

    def update_reagent_list(self) -> None:
        """Update the display of reagent items."""
        items = []
        
        # Create heading for solid reagents if any exist
        if self.data_manager.data["solid reagents"]:
            items.append(widgets.HTML(
                "<h3 style='color: #3F704D; margin: 10px 0 5px 0; border-bottom: 2px solid #90BE6D;'>Solid Reagents</h3>"
            ))
            for reagent in self.data_manager.data["solid reagents"]:
                item = UIComponents.create_reagent_item(
                    reagent, 
                    is_solid=True,
                    on_edit=self.edit_reagent,
                    on_delete=self.delete_reagent
                )
                items.append(item)
        
        # Create heading for liquid reagents if any exist
        if self.data_manager.data["liquid reagents"]:
            items.append(widgets.HTML(
                "<h3 style='color: #3A5D9F; margin: 15px 0 5px 0; border-bottom: 2px solid #577590;'>Liquid Reagents</h3>"
            ))
            for reagent in self.data_manager.data["liquid reagents"]:
                item = UIComponents.create_reagent_item(
                    reagent, 
                    is_solid=False,
                    on_edit=self.edit_reagent,
                    on_delete=self.delete_reagent
                )
                items.append(item)
        
        # If no reagents, show a message
        if not items:
            items.append(widgets.HTML(
                "<div style='text-align: center; padding: 20px; color: #666; font-style: italic;'>"
                "No reagents added yet. Go to the 'Add Reagents' tab to add reagents."
                "</div>"
            ))
        
        # Update the reagent list with the items
        self.reagent_list.children = tuple(items)

    def save_reagent(self, new_reagent, old_reagent=None, specified_type=None):
        """Save a reagent to the data."""
        try:
            # Validate we have the minimum required fields
            required_fields = ["name", "inChi", "molecular weight (in g/mol)", "eq", "syringe"]
            missing_fields = [field for field in required_fields if field not in new_reagent]
            
            if missing_fields:
                return False
                
            if new_reagent["name"].strip() == "":
                return False
            
            # Determine reagent type with better error handling
            reagent_type = None
            
            if specified_type:
                # Use explicitly specified type (from PubChem import)
                reagent_type = specified_type
            elif old_reagent:
                # For editing, get the type from data manager
                reagent_type = self.data_manager.get_reagent_type(old_reagent)
            else:
                # For new reagent, check if it has a density field
                reagent_type = "liquid" if "density (in g/mL)" in new_reagent else "solid"
            
            # Remove special type field if it exists
            if "_reagent_type" in new_reagent:
                del new_reagent["_reagent_type"]
                
            # Create a deep copy of the reagent to avoid reference issues
            import copy
            reagent_copy = copy.deepcopy(new_reagent)
            
            # Force the values to be the correct types
            reagent_copy["molecular weight (in g/mol)"] = float(reagent_copy["molecular weight (in g/mol)"])
            reagent_copy["eq"] = float(reagent_copy["eq"])
            reagent_copy["syringe"] = int(reagent_copy["syringe"])
            if "density (in g/mL)" in reagent_copy:
                reagent_copy["density (in g/mL)"] = float(reagent_copy["density (in g/mL)"])
            
            # Ensure we have a valid reagent type
            if reagent_type not in ["solid", "liquid"]:
                return False
            
            # Add or update the reagent in the data manager
            if old_reagent:
                self.data_manager.update_reagent(old_reagent, reagent_copy, reagent_type)
            else:
                self.data_manager.add_reagent(reagent_copy, reagent_type)
            
            # Update the reagent list
            self.update_reagent_list()
            
            # Refresh the final details tab with updated data
            self.refresh_final_details_tab()
            
            # Switch to Current Reagents tab to show the new reagent
            self.tab_container.selected_index = 1
            
            return True
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False

    def delete_reagent(self, reagent):
        """Remove a reagent from the data."""
        self.data_manager.delete_reagent(reagent)
        
        # Update the display
        self.update_reagent_list()

    def edit_reagent(self, reagent):
        """Open the form to edit an existing reagent."""
        # Determine reagent type
        reagent_type = self.data_manager.get_reagent_type(reagent)
        
        # Switch to the Add Reagents tab
        self.tab_container.selected_index = 0
        
        # Select the appropriate accordion section
        accordion_index = 0 if reagent_type == "solid" else 1
        accordion = self.add_reagents_tab.children[1]  # Get the accordion widget
        accordion.selected_index = accordion_index
        
        # Create a new form with the reagent data
        form = ReagentFormHandler.create_reagent_form(
            reagent_type, 
            reagent=reagent,
            on_save=self.save_reagent
        )
        
        # Replace the existing form by creating a new tuple
        new_children = list(accordion.children)
        new_children[accordion_index] = form
        accordion.children = tuple(new_children)

    def lookup_chemical(self, name, smiles_input, inchi_input, inchikey_input, mw_input, update_callback):
        """Look up chemical structure by name or SMILES."""
        if smiles_input.value:
            update_callback()
        elif name:
            # Try to lookup by name
            results = self.pubchem_service.search(name, 'name')
            if results:
                compound = results[0]
                smiles_input.value = compound['smiles']
                inchi_input.value = compound['inchi']
                inchikey_input.value = compound['inchikey']
                mw_input.value = compound['molecular_weight']
                update_callback()

    def import_from_pubchem_solid(self, compound):
        """Import PubChem data as a solid reagent."""
        self.import_from_pubchem(compound, "solid")
        
    def import_from_pubchem_liquid(self, compound):
        """Import PubChem data as a liquid reagent."""
        self.import_from_pubchem(compound, "liquid")

    def import_from_pubchem(self, compound, reagent_type):
        """Import PubChem data into a new reagent form."""
        # Switch to Add Reagents tab
        self.tab_container.selected_index = 0
        
        # Select the appropriate accordion section
        accordion_index = 0 if reagent_type == "solid" else 1
        accordion = self.add_reagents_tab.children[1]  # Get the accordion widget
        accordion.selected_index = accordion_index
        
        # Create a new reagent from the compound data
        # Strip InChI= prefix from the InChI string if it exists
        inchi = compound['inchi']
        if inchi and inchi.startswith("InChI="):
            inchi = inchi[6:]  # Remove 'InChI=' prefix
            
        new_reagent = {
            "name": compound['name'],
            "inChi": inchi,
            "SMILES": compound['smiles'],
            "inChi Key": compound['inchikey'],
            "molecular weight (in g/mol)": compound['molecular_weight'],
            "eq": 1.0,  # Default to 1.0 equivalents
            "syringe": 1,  # Default syringe number
            "_reagent_type": reagent_type  # Add explicit type marking
        }
        
        # Add density for liquids (from PubChem if available, otherwise default)
        has_density = False
        warning_message = None
        
        if reagent_type == "liquid":
            if compound.get('density') and compound['density'] > 0:
                new_reagent["density (in g/mL)"] = compound['density']
                has_density = True
            else:
                new_reagent["density (in g/mL)"] = 1.0
                # Set warning message for liquid with no density
                warning_message = "No density value found in PubChem, using default (1.0 g/mL). Please change this accordingly!"
        
        # Create a new form with the compound data
        form = ReagentFormHandler.create_reagent_form(
            reagent_type, 
            reagent=new_reagent,
            on_save=lambda new, old=None: self.save_reagent(new, old, specified_type=reagent_type),
            warning_message=warning_message  # Pass warning message to form
        )
        
        # Replace the existing form with a new tuple
        new_children = list(accordion.children)
        new_children[accordion_index] = form
        accordion.children = tuple(new_children)
        
        # Display success message - simplified to avoid redundant density warning
        success_message = f"<p style='color: green;'>Data imported as {reagent_type}."
        if reagent_type == "liquid" and has_density:
            success_message += f" Density value ({compound['density']} g/mL) retrieved from PubChem."
        success_message += " Please complete any remaining fields.</p>"
        self.search_status.value = success_message

    def process_final_details(self, mass_scale, concentration, solvent, message_area):
        """Process the final details and submit the data."""
        try:
            # Update data with form values
            self.data_manager.update_final_details(mass_scale, concentration, solvent)
            
            # Validate that at least one reagent has eq=1.0
            if not self.data_manager.has_limiting_reagent():
                raise ValueError("At least one reagent must have an equivalent (eq) value of 1.0")
            
            # Remove the form widgets
            self.main_container.layout.display = 'none'
            
            # Process data
            import IPython.display as display
            import time
            from mechwolf.DataEntry.ReagentUI.ProcessData import process_data
            
            # Force a complete reset of output
            display.clear_output(wait=True)
            display.display(display.HTML("<h3>Processing Data:</h3>"))
            
            # Small delay to ensure file operations complete
            time.sleep(0.5)
            
            # Process the data
            process_data(self.data_file)
            return True
            
        except ValueError as e:
            # Display error message
            message_area.value = f"<p style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>Error: {str(e)}</p>"
            return False

    def refresh_final_details_tab(self):
        """Refresh the final details tab with current data."""
        # Create a new final details form with the latest data
        new_form = FinalDetailsFormHandler.create_final_details_form(
            self.data_manager.data,
            on_submit=self.process_final_details
        )
        
        # Replace the existing form
        self.final_details_tab.children = (
            widgets.HTML("<h4>Final Details and Submission</h4>"),
            new_form
        )

    def run(self) -> None:
        """Run the application."""
        # If there's no data, create the widgets
        if not self.data_manager.data["solid reagents"] and not self.data_manager.data["liquid reagents"]:
            self.setup_ui()
        else:
            # First show the current data as a table
            from mechwolf.DataEntry.ReagentUI.ProcessData import process_data
            process_data(self.data_file)
            
            # Then ask if user wants to edit or proceed
            display(widgets.HTML("<h3>What would you like to do with this data?</h3>"))
            edit_btn = widgets.Button(
                description="Edit Data", 
                button_style="info",
                style={"button_color": "#3A5D9F"}
            )
            continue_btn = widgets.Button(
                description="Continue without editing", 
                button_style="success",
                style={"button_color": "#3F704D"}
            )
            
            def on_edit(b):
                clear_output(wait=True)
                self.setup_ui()
            
            def on_continue(b):
                # User chooses to use data as is
                pass
                
            edit_btn.on_click(on_edit)
            continue_btn.on_click(on_continue)
            
            display(widgets.HBox([edit_btn, continue_btn], 
                                layout=widgets.Layout(margin="20px 0")))

if __name__ == "__main__":
    data_file = input("Enter the JSON file name: ").strip()
    app = ReagentInputForm(data_file)
    app.run()
