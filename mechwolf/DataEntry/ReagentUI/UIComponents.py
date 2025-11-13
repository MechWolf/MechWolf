"""UI components for reagent entry forms."""
import ipywidgets as widgets
from typing import Dict, Any, Callable
from .StructureVisualization import StructureVisualizer

class UIComponents:
    """Factory for creating UI components."""
    
    @staticmethod
    def create_reagent_item(reagent: Dict[str, Any], is_solid: bool, 
                            on_edit: Callable, on_delete: Callable) -> widgets.Widget:
        """
        Create a widget to display a reagent with edit/delete buttons.
        
        Parameters:
        -----------
        reagent : dict
            Reagent data
        is_solid : bool
            Whether the reagent is a solid
        on_edit : callable
            Callback for edit button
        on_delete : callable
            Callback for delete button
            
        Returns:
        --------
        ipywidgets.Widget
            Widget displaying the reagent
        """
        bg_color = "#F0F7F4" if is_solid else "#EFF7FF"  # Light green for solids, light blue for liquids
        
        # Create structure visualization if possible
        structure_widget = StructureVisualizer.get_structure_image(
            reagent.get("SMILES", ""), 
            size=(120, 120)
        )
        
        # Style for reagent item
        item_style = f"""
        <div style="padding: 8px; background-color: {bg_color}; border-radius: 4px; margin-bottom: 4px;">
            <h4 style="margin: 0 0 5px 0;">{reagent['name']}</h4>
            <div style="display: flex; flex-direction: row;">
                <div style="flex: 1;">
                    <p style="margin: 2px 0;"><b>Eq:</b> {reagent['eq']}</p>
                    <p style="margin: 2px 0;"><b>MW:</b> {reagent['molecular weight (in g/mol)']} g/mol</p>
                </div>
                <div style="flex: 1;">
                    <p style="margin: 2px 0;"><b>Syringe:</b> {reagent['syringe']}</p>
                    {f'<p style="margin: 2px 0;"><b>Density:</b> {reagent.get("density (in g/mL)", "N/A")} g/mL</p>' if not is_solid else ''}
                </div>
            </div>
        </div>
        """
        
        # HTML widget for the reagent details
        html_widget = widgets.HTML(item_style)
        
        # Create buttons
        edit_button = widgets.Button(
            description="Edit",
            button_style="info",
            layout=widgets.Layout(width="60px"),
            style={"button_color": "#1E3A8A"}
        )
        
        delete_button = widgets.Button(
            description="Delete",
            button_style="danger",
            layout=widgets.Layout(width="70px"),
            style={"button_color": "#D72638"}
        )
        
        # Setup callbacks
        edit_button.on_click(lambda b: on_edit(reagent))
        delete_button.on_click(lambda b: on_delete(reagent))
        
        # Container for buttons
        button_container = widgets.VBox(
            [edit_button, delete_button],
            layout=widgets.Layout(margin="0 0 0 10px", align_items="flex-start")
        )
        
        # Return an HBox containing the structure, HTML and buttons
        if structure_widget:
            return widgets.HBox(
                [structure_widget, html_widget, button_container],
                layout=widgets.Layout(
                    margin="2px 0",
                    align_items="center",
                    border=f"1px solid {'#90BE6D' if is_solid else '#577590'}",
                    border_radius="5px",
                    padding="5px"
                )
            )
        else:
            return widgets.HBox(
                [html_widget, button_container],
                layout=widgets.Layout(
                    margin="2px 0",
                    align_items="center",
                    border=f"1px solid {'#90BE6D' if is_solid else '#577590'}",
                    border_radius="5px",
                    padding="5px"
                )
            )
    
    @staticmethod
    def create_search_result_widget(compound: Dict[str, Any], 
                                   on_import_solid: Callable, 
                                   on_import_liquid: Callable) -> widgets.Widget:
        """
        Create a widget to display a search result with import buttons.
        
        Parameters:
        -----------
        compound : dict
            Compound data
        on_import_solid : callable
            Callback for import as solid button
        on_import_liquid : callable
            Callback for import as liquid button
            
        Returns:
        --------
        ipywidgets.Widget
            Widget displaying the search result
        """
        # Generate structure image
        structure_img = StructureVisualizer.get_structure_image(
            compound.get('smiles', ''), 
            size=(150, 150)
        )
        
        # Create info widget
        info_html = f"""
        <div style="padding-left: 10px;">
            <h4>{compound['name'] or 'Unknown'}</h4>
            <p><b>Formula:</b> {compound['formula']}</p>
            <p><b>Molecular Weight:</b> {compound['molecular_weight']} g/mol</p>
            <p><b>InChI Key:</b> {compound['inchikey']}</p>
            <p><b>SMILES:</b> {compound['smiles']}</p>
        </div>
        """
        
        info_widget = widgets.HTML(info_html)
        
        # Create import buttons
        import_solid_button = widgets.Button(
            description="Import as Solid",
            button_style="success",
            style={"button_color": "#3F704D"}
        )
        
        import_liquid_button = widgets.Button(
            description="Import as Liquid",
            button_style="info",
            style={"button_color": "#3A5D9F"}
        )
        
        # Set up callbacks
        import_solid_button.on_click(lambda b: on_import_solid(compound))
        import_liquid_button.on_click(lambda b: on_import_liquid(compound))
        
        # Arrange buttons
        buttons = widgets.VBox([
            import_solid_button,
            import_liquid_button
        ])
        
        # Create result container with structure + info + buttons
        if structure_img:
            result = widgets.HBox([
                structure_img,
                info_widget,
                buttons
            ])
        else:
            result = widgets.HBox([
                info_widget,
                buttons
            ])
        
        return widgets.VBox([
            result,
            widgets.HTML("<hr style='margin: 10px 0;'>")
        ], layout=widgets.Layout(margin="5px 0"))
