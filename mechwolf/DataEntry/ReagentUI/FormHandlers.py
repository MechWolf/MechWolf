"""Form handlers for reagent entry forms."""
import ipywidgets as widgets
from typing import Dict, Any, Optional, Callable
from .StructureVisualization import StructureVisualizer
from mechwolf.DataEntry.ReagentUI.ReagentUtils import validate_reagent_data

class ReagentFormHandler:
    """Handler for reagent entry forms."""
    
    @staticmethod
    def create_form_field(
        widget: widgets.Widget, 
        tooltip_text: str, 
        error_style: bool = False
    ) -> widgets.VBox:
        """
        Create a form field with tooltip.
        
        Parameters:
        -----------
        widget : widgets.Widget
            Input widget
        tooltip_text : str
            Text for tooltip
        error_style : bool
            Whether to style the tooltip as an error
            
        Returns:
        --------
        widgets.VBox
            Container with widget and tooltip
        """
        tooltip_color = "red" if error_style else "#666"
        tooltip_weight = "bold" if error_style else "normal"
        
        tooltip = widgets.HTML(
            f"<span style='font-size: 0.8em; color: {tooltip_color}; font-weight: {tooltip_weight};'>{tooltip_text}</span>"
        )
        
        if error_style:
            widget.layout.border = "2px solid red"
            
        return widgets.VBox([widget, tooltip])
    
    @staticmethod
    def create_reagent_form(reagent_type: str, 
                           reagent: Optional[Dict[str, Any]] = None,
                           on_save: Callable = None,
                           warning_message: str = None) -> widgets.Widget:
        """
        Create a form for adding or editing a reagent.
        
        Parameters:
        -----------
        reagent_type : str
            Type of reagent ('solid' or 'liquid')
        reagent : dict, optional
            Existing reagent data for editing
        on_save : callable
            Callback for save button
        warning_message : str, optional
            Warning message to display in the form
            
        Returns:
        --------
        ipywidgets.Widget
            Form widget
        """
        # Set background color based on reagent type
        bg_color = "#F0F7F4" if reagent_type == "solid" else "#EFF7FF"
        
        # Create form widgets
        form_title = widgets.HTML(
            f"<h4 style='color: {'#3F704D' if reagent_type == 'solid' else '#3A5D9F'};'>{'Edit' if reagent else 'Add'} {reagent_type.capitalize()} Reagent</h4>"
        )
        
        # Error message area
        error_area = widgets.HTML("")
        
        # Warning message area (if provided)
        warning_area = widgets.HTML("")
        if warning_message and reagent_type == "liquid":
            warning_area.value = f"""
            <div style='color: red; font-weight: bold; background-color: #FFEEEE; 
                        padding: 8px; margin: 10px 0; border-radius: 4px; 
                        border: 1px solid #FFD2D2;'>
              Warning: {warning_message}
            </div>
            """
        
        # Create input fields with validation styles
        name_input = widgets.Text(
            value=reagent["name"] if reagent else "",
            description="Name:",
            layout=widgets.Layout(width="80%")
        )
        
        inchi_input = widgets.Text(
            value=reagent["inChi"] if reagent else "",
            description="InChi:",
            layout=widgets.Layout(width="80%")
        )
        
        smiles_input = widgets.Text(
            value=reagent["SMILES"] if reagent else "",
            description="SMILES:",
            layout=widgets.Layout(width="80%")
        )
        
        inchikey_input = widgets.Text(
            value=reagent["inChi Key"] if reagent else "",
            description="InChi Key:",
            layout=widgets.Layout(width="80%")
        )
        
        mw_input = widgets.FloatText(
            value=reagent["molecular weight (in g/mol)"] if reagent else 0,
            description="MW (g/mol):",
            layout=widgets.Layout(width="80%")
        )
        
        eq_input = widgets.FloatText(
            value=reagent["eq"] if reagent else 0,
            description="Equivalents:",
            layout=widgets.Layout(width="80%")
        )
        
        syringe_input = widgets.IntText(
            value=reagent["syringe"] if reagent else 0,
            description="Syringe:",
            layout=widgets.Layout(width="80%")
        )
        
        # Create form fields with tooltips using the helper method
        form_fields = [
            form_title,
            error_area
        ]
        
        # Add warning area if there's a warning message
        if warning_message and reagent_type == "liquid":
            form_fields.append(warning_area)
            
        # Add standard form fields with tooltips
        form_fields.extend([
            ReagentFormHandler.create_form_field(
                name_input, "Required: Chemical name"),
            ReagentFormHandler.create_form_field(
                inchi_input, "Example: InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"),
            ReagentFormHandler.create_form_field(
                smiles_input, "Example: O=C[C@@H]([C@H]([C@@H]([C@@H](CO)O)O)O)O (glucose)"),
            ReagentFormHandler.create_form_field(
                inchikey_input, "Example: LFQSCWFLJHTTHZ-UHFFFAOYSA-N"),
            ReagentFormHandler.create_form_field(
                mw_input, "Required: Must be > 0"),
            ReagentFormHandler.create_form_field(
                eq_input, "Required: Must be > 0. Set to 1.0 for limiting reagent."),
            ReagentFormHandler.create_form_field(
                syringe_input, "Required: Must be > 0")
        ])
        
        # Add density field for liquid reagents
        if reagent_type == "liquid":
            density_input = widgets.FloatText(
                value=reagent["density (in g/mL)"] if reagent else 0,
                description="Density (g/mL):",
                layout=widgets.Layout(width="80%")
            )
            
            # Add density field with appropriate styling based on warning status
            density_tooltip = "Required for liquids: Please update this value!" if warning_message else "Required for liquids: Must be > 0"
            form_fields.append(
                ReagentFormHandler.create_form_field(
                    density_input, density_tooltip, error_style=bool(warning_message)
                )
            )
        
        # Add structure visualization area
        structure_area = widgets.Output(
            layout=widgets.Layout(width="200px", height="200px")
        )
        
        # Function to update structure visualization
        def update_structure(change=None):
            structure_area.clear_output()
            with structure_area:
                from IPython.display import display
                if smiles_input.value:
                    vis = StructureVisualizer.get_structure_image(smiles_input.value, size=(200, 200))
                    if vis:
                        display(vis)
                    else:
                        print("Could not render structure.\nCheck SMILES format.")
                else:
                    pass  # Empty output
        
        # Connect update to SMILES field
        smiles_input.observe(update_structure, names='value')
        
        # Add structure visualization
        form_fields.append(widgets.VBox([
            widgets.HTML("<h4>Structure Preview</h4>"),
            structure_area
        ], layout=widgets.Layout(
            align_items="center",
            border="1px solid #ddd",
            margin="10px 0",
            padding="10px"
        )))
        
        # Create save button
        save_button = widgets.Button(
            description="Save Reagent",
            button_style="success",
            layout=widgets.Layout(width="auto"),
            style={"button_color": "#3F704D" if reagent_type == "solid" else "#3A5D9F"}
        )
        
        # Just add the save button (removed debug button)
        form_fields.append(save_button)
        
        # Create form container with color coding
        form = widgets.VBox(
            form_fields,
            layout=widgets.Layout(
                border=f"1px solid {'#90BE6D' if reagent_type == 'solid' else '#577590'}",
                padding="15px",
                margin="10px 0",
                background_color=bg_color
            )
        )
        
        # Update structure if SMILES is available
        if smiles_input.value:
            update_structure()
        
        # Set up callback for save button
        if on_save:
            def validate_and_save(b):
                # Collect form data
                # Clean the InChI value by removing the InChI= prefix if present
                inchi_value = inchi_input.value
                if inchi_value and inchi_value.startswith("InChI="):
                    inchi_value = inchi_value[6:]  # Remove 'InChI=' prefix
                
                new_reagent = {
                    "name": name_input.value,
                    "inChi": inchi_value,  # Use the cleaned InChI value
                    "SMILES": smiles_input.value,
                    "inChi Key": inchikey_input.value,
                    "molecular weight (in g/mol)": mw_input.value,
                    "eq": eq_input.value,
                    "syringe": syringe_input.value
                }
                
                # Add density for liquid reagents
                if reagent_type == "liquid" and 'density_input' in locals():
                    new_reagent["density (in g/mL)"] = density_input.value
                
                # Validate data
                validation_errors = validate_reagent_data(new_reagent, reagent_type)
                
                # Reset error displays
                error_area.value = ""
                
                # If errors, show them
                if validation_errors:
                    error_html = "<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px; margin-bottom: 10px;'>"
                    error_html += "<b>Please correct the following errors:</b><ul>"
                    for field, message in validation_errors.items():
                        error_html += f"<li>{message}</li>"
                    error_html += "</ul></div>"
                    error_area.value = error_html
                    return
                
                try:
                    # Clear any existing error message
                    error_area.value = ""
                    
                    # Call the save callback with the new reagent and old reagent (if editing)
                    success = on_save(new_reagent, reagent)
                    
                    if success:
                        # Show success message
                        error_area.value = "<div style='color: green; padding: 10px; background-color: #EEFFEE; border-radius: 5px; margin-bottom: 10px;'><b>Reagent saved successfully!</b></div>"
                        
                        # Avoid clearing the form when editing (only clear for new entries)
                        if not reagent:  # Only clear if this is a new entry (not editing)
                            name_input.value = ""
                            inchi_input.value = ""
                            smiles_input.value = ""
                            inchikey_input.value = ""
                            mw_input.value = 0
                            eq_input.value = 0
                            syringe_input.value = 0
                            if reagent_type == "liquid" and 'density_input' in locals():
                                density_input.value = 0
                    else:
                        error_area.value = "<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px; margin-bottom: 10px;'><b>Failed to save reagent. Check console for errors.</b></div>"
                except Exception as e:
                    error_area.value = f"<div style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px; margin-bottom: 10px;'><b>Error: {str(e)}</b></div>"
                    import traceback
                    traceback.print_exc()
            
            save_button.on_click(validate_and_save)
        
        return form

class FinalDetailsFormHandler:
    """Handler for final details form."""
    
    @staticmethod
    def create_final_details_form(data: Dict[str, Any], on_submit: Callable) -> widgets.Widget:
        """
        Create a form for final details.
        
        Parameters:
        -----------
        data : dict
            Current data
        on_submit : callable
            Callback for submit button
            
        Returns:
        --------
        ipywidgets.Widget
            Form widget
        """
        # Get existing values if any
        mass_scale_value = data.get("mass scale (in mg)", None)
        concentration_value = data.get("concentration (in mM)", None)
        solvent_value = data.get("solvent", "")
        
        # Create form widgets
        form_title = widgets.HTML("<h4>Final Details</h4>")
        
        # Error/message display area
        message_area = widgets.HTML("")
        
        # Find the limiting reagent (eq = 1.0)
        limiting_reagent = None
        limiting_reagent_mw = None
        
        for reagent in data.get("solid reagents", []) + data.get("liquid reagents", []):
            if abs(reagent.get("eq", 0) - 1.0) < 1e-6:
                limiting_reagent = reagent["name"]
                limiting_reagent_mw = reagent["molecular weight (in g/mol)"]
                break
        
        # Display the limiting reagent - Fix the f-string syntax
        if limiting_reagent:
            reagent_html = f"<p><b>Limiting Reagent:</b> {limiting_reagent}</p>"
        else:
            reagent_html = "<p><b>Limiting Reagent:</b> <span style=\"color:red\">None selected (set eq=1.0 for limiting reagent)</span></p>"
        
        limiting_reagent_display = widgets.HTML(value=reagent_html)
        
        mass_scale_input = widgets.FloatText(
            value=mass_scale_value,
            description="Mass scale (mg):",
            layout=widgets.Layout(width="80%")
        )
        
        concentration_input = widgets.FloatText(
            value=concentration_value,
            description="Concentration (mM):",
            layout=widgets.Layout(width="80%")
        )
        
        # Add display for calculated volume
        volume_display = widgets.HTML(
            value="<p><b>Volume needed:</b> Calculate by entering values above</p>"
        )
        
        # Function to calculate and update volume
        def update_volume(*args):
            try:
                mass_scale = mass_scale_input.value
                concentration = concentration_input.value
                
                if not limiting_reagent_mw or mass_scale <= 0 or concentration <= 0:
                    volume_display.value = "<p><b>Volume needed:</b> Please enter valid mass scale and concentration values</p>"
                    return
                
                # Calculate moles of limiting reagent (mg to mmol)
                moles_limiting = mass_scale / limiting_reagent_mw
                
                # Calculate volume in mL (convert from mM to M)
                volume_solution = moles_limiting / (concentration / 1000)
                
                volume_display.value = f"<p><b>Volume needed:</b> {volume_solution:.4f} mL</p>"
            except Exception as e:
                volume_display.value = f"<p><b>Volume needed:</b> Error in calculation: {str(e)}</p>"
        
        # Observe changes to update volume calculation
        mass_scale_input.observe(update_volume, names='value')
        concentration_input.observe(update_volume, names='value')
        
        solvent_input = widgets.Text(
            value=solvent_value,
            description="Solvents:",
            layout=widgets.Layout(width="80%")
        )
        
        submit_button = widgets.Button(
            description="Process Data",
            button_style="success",
            layout=widgets.Layout(width="auto")
        )
        
        # Create form container
        form = widgets.VBox(
            [
                form_title,
                message_area,
                limiting_reagent_display,
                mass_scale_input,
                concentration_input,
                volume_display,
                solvent_input,
                submit_button
            ],
            layout=widgets.Layout(
                border="1px solid #ddd",
                padding="10px",
                margin="10px 0"
            )
        )
        
        # Set up button callback
        def submit_handler(b):
            try:
                # Get form values
                mass_scale = mass_scale_input.value
                concentration = concentration_input.value
                solvent = solvent_input.value
                
                # Call the submit callback with the form values
                success = on_submit(mass_scale, concentration, solvent, message_area)
                
                # If not successful, the message will be displayed by the callback
                
            except Exception as e:
                # Display error message
                message_area.value = f"<p style='color: red; padding: 10px; background-color: #FFEEEE; border-radius: 5px;'>Error: {str(e)}</p>"
        
        submit_button.on_click(submit_handler)
        
        # Initial volume calculation if all values are available
        if mass_scale_value and concentration_value and limiting_reagent_mw:
            update_volume()
        
        return form
    