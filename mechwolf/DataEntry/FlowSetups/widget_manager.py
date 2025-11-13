import ipywidgets as widgets
from typing import Any, Dict, Union

"""
Manages the creation and handling of various widgets for a component application.
Attributes:
    app (object): The component application instance.
    widgets (dict): A dictionary to store created widgets.
Methods:
    __init__(component_app):
        Initializes the WidgetManager with the given component application.
    create_text_input(placeholder, width='50%'):
        Helper to create standardized text input widgets.
    create_vessel_widgets(num_vessels):
        Creates widgets for a variable number of vessels.
    create_tube_widgets(num_tubes):
        Creates widgets for a variable number of reaction tubes.
    create_mixer_widgets(num_mixers):
        Creates widgets for a variable number of mixers.
    create_coil_widgets(num_coils):
        Creates widgets for a variable number of coils using letters.
    create_setup_button():
        Creates the setup button with custom styling.
    create_all_widgets(num_vessels=3, num_tubes=1, num_coils=2, num_mixers=1):
        Creates all widgets with configurable numbers of components.
    get_widget_values():
        Gets all widget values as a dictionary.
    prefill_values(config):
        Prefills widgets with existing configuration.
    _prefill_tubes(config):
        Helper method to prefill tube widgets.
    _prefill_mixers(config):
        Helper method to prefill mixer widgets.
    _prefill_coils(config):
        Helper method to prefill coil widgets.
"""
from IPython.display import display


class WidgetManager:
    def __init__(self, component_app: Any) -> None:
        self.app: Any = component_app
        self.widgets: Dict[str, Union[widgets.Widget, Dict[str, int]]] = {}

    def create_text_input(self, placeholder: str, width: str = "50%") -> widgets.Text:
        """Helper to create standardized text input"""
        return widgets.Text(placeholder=placeholder, layout=widgets.Layout(width=width))

    def create_vessel_widgets(self, num_vessels: int) -> None:
        """Create widgets for variable number of vessels"""
        # Create regular vessel widgets
        for i in range(1, num_vessels):
            self.widgets[f"vessel{i}_name"] = self.create_text_input(
                f"Enter Vessel {i} name"
            )
            self.widgets[f"vessel{i}_desc"] = self.create_text_input(
                f"Enter Vessel {i} description"
            )

        # Create product vessel widgets (always last)
        self.widgets["product_vessel_name"] = self.create_text_input(
            "Enter Product Vessel name"
        )
        self.widgets["product_vessel_desc"] = self.create_text_input(
            "Enter Product Vessel description"
        )

    def create_tube_widgets(self, num_tubes: int) -> None:
        """Create widgets for variable number of reaction tubes"""
        for i in range(1, num_tubes + 1):
            self.widgets[f"reaction_tube{i}_id"] = self.create_text_input(
                f"Reaction Tube {i} Inner Diameter (ID)"
            )
            self.widgets[f"reaction_tube{i}_od"] = self.create_text_input(
                f"Reaction Tube {i} Outer Diameter (OD)"
            )
            self.widgets[f"reaction_tube{i}_material"] = self.create_text_input(
                f"Reaction Tube {i} Material"
            )

    def create_mixer_widgets(self, num_mixers: int) -> None:
        """Create widgets for variable number of mixers"""
        self.widgets["using_mixer"] = widgets.Checkbox(
            value=False, description="Using Mixer"
        )

        for i in range(1, num_mixers + 1):
            self.widgets[f"mixer{i}_tube_id"] = self.create_text_input(
                f"Mixer {i} Inner Diameter (ID)"
            )
            self.widgets[f"mixer{i}_tube_od"] = self.create_text_input(
                f"Mixer {i} Outer Diameter (OD)"
            )
            self.widgets[f"mixer{i}_tube_material"] = self.create_text_input(
                f"Mixer {i} Tube Material"
            )

    def create_coil_widgets(self, num_coils: int) -> None:
        """Create widgets for variable number of coils using letters"""
        coil_letters = ["a", "x", "b", "y"]  # Define order of coil letters
        for i in range(num_coils):
            letter = coil_letters[i]
            self.widgets[f"coil_{letter}"] = self.create_text_input(
                f"Coil {letter.upper()} length"
            )
            self.widgets[f"coil_{letter}_index"] = letter  # Store the index/letter

    def create_setup_button(self) -> widgets.Button:
        """Create the setup button with custom styling"""
        return widgets.Button(
            description="Create/Save Setup",
            style=widgets.ButtonStyle(button_color="#990000", text_color="#EEEDEB"),
            layout=widgets.Layout(
                width="150px", margin="10px 0px 0px 0px", align_items="flex-start"
            ),
        )

    def create_all_widgets(
        self, num_vessels: int = 3, num_tubes: int = 1, num_coils: int = 2, num_mixers: int = 1
    ) -> Dict[str, Union[widgets.Widget, Dict[str, int]]]:
        """Create all widgets with configurable numbers of components"""
        # Store component counts
        self.widgets["component_counts"] = {
            "vessels": num_vessels,
            "tubes": num_tubes,
            "coils": num_coils,
            "mixers": num_mixers,
        }

        # Create apparatus name widget
        self.widgets["apparatus_name"] = self.create_text_input("Enter apparatus name")

        # Create all component widgets
        self.create_vessel_widgets(num_vessels)
        self.create_tube_widgets(num_tubes)
        self.create_mixer_widgets(num_mixers)
        self.create_coil_widgets(num_coils)

        # Create setup button
        self.setup_button = self.create_setup_button()
        self.setup_button.on_click(self.app.create_setup)

        # Create widget container with all widgets
        widget_list = [widgets.HTML("<hr>")]

        # Add apparatus name
        widget_list.extend(
            [widgets.Label("Apparatus Name:"), self.widgets["apparatus_name"]]
        )

        # Add vessel widgets
        for i in range(1, num_vessels):
            widget_list.extend(
                [
                    widgets.Label(f"Vessel {i} Details:"),
                    self.widgets[f"vessel{i}_name"],
                    self.widgets[f"vessel{i}_desc"],
                ]
            )

        # Add product vessel
        widget_list.extend(
            [
                widgets.Label("Product Vessel Details:"),
                self.widgets["product_vessel_name"],
                self.widgets["product_vessel_desc"],
            ]
        )

        # Add tube widgets
        for i in range(1, num_tubes + 1):
            widget_list.extend(
                [
                    widgets.Label(f"Reaction Tube {i} Details:"),
                    self.widgets[f"reaction_tube{i}_id"],
                    self.widgets[f"reaction_tube{i}_od"],
                    self.widgets[f"reaction_tube{i}_material"],
                ]
            )

        # Add mixer widgets
        widget_list.append(self.widgets["using_mixer"])
        for i in range(1, num_mixers + 1):
            widget_list.extend(
                [
                    widgets.Label(f"Mixer {i} Tube Details (if using mixer):"),
                    self.widgets[f"mixer{i}_tube_id"],
                    self.widgets[f"mixer{i}_tube_od"],
                    self.widgets[f"mixer{i}_tube_material"],
                ]
            )

        # Add coil widgets
        widget_list.append(widgets.Label("Coil Lengths:"))
        coil_letters = ["a", "x", "b", "y"][:num_coils]  # Get only needed letters
        for letter in coil_letters:
            widget_list.append(self.widgets[f"coil_{letter}"])

        # Add setup button
        widget_list.append(self.setup_button)

        # Create and display container
        self.widget_container = widgets.VBox(
            widget_list, layout=widgets.Layout(width="100%")
        )
        display(self.widget_container)

        return self.widgets

    def get_widget_values(self) -> Dict[str, Union[str, bool]]:
        """Get all widget values as a dictionary"""
        values: Dict[str, Union[str, bool]] = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, dict):  # Skip component_counts dictionary
                continue
            if isinstance(widget, widgets.Checkbox):
                values[key] = widget.value
            elif isinstance(widget, widgets.Text):
                values[key] = widget.value or ""
        return values

    def prefill_values(self, config: Dict[str, Any]) -> None:
        """Prefill widgets with existing configuration"""
        try:
            # Update apparatus name
            self.widgets["apparatus_name"].value = config.get("apparatus_name", "")

            # Update vessel values
            vessels = config.get("vessels", [])
            for i, vessel in enumerate(vessels[:-1], 1):  # All but last vessel
                self.widgets[f"vessel{i}_name"].value = vessel.get("name", "")
                self.widgets[f"vessel{i}_desc"].value = vessel.get("description", "")

            # Update product vessel (last vessel)
            if vessels:
                self.widgets["product_vessel_name"].value = vessels[-1].get("name", "")
                self.widgets["product_vessel_desc"].value = vessels[-1].get(
                    "description", ""
                )

            # Update remaining widgets based on configuration
            self._prefill_tubes(config)
            self._prefill_mixers(config)
            self._prefill_coils(config)

        except Exception as e:
            print(f"Error prefilling values: {str(e)}")
            self._initialize_empty_values()

    def _prefill_tubes(self, config: Dict[str, Any]) -> None:
        """Helper method to prefill tube widgets"""
        tubes = config.get("tubes", {}).get("reaction", {})
        num_tubes = self.widgets["component_counts"]["tubes"]
        for i in range(1, num_tubes + 1):
            self.widgets[f"reaction_tube{i}_id"].value = tubes.get("ID", "")
            self.widgets[f"reaction_tube{i}_od"].value = tubes.get("OD", "")
            self.widgets[f"reaction_tube{i}_material"].value = tubes.get("material", "")

    def _prefill_mixers(self, config: Dict[str, Any]) -> None:
        """Helper method to prefill mixer widgets"""
        self.widgets["using_mixer"].value = config.get("using_mixer", False)
        if config.get("using_mixer"):
            mixer_config = config.get("tubes", {}).get("mixer", {})
            num_mixers = self.widgets["component_counts"]["mixers"]
            for i in range(1, num_mixers + 1):
                self.widgets[f"mixer{i}_tube_id"].value = mixer_config.get("ID", "")
                self.widgets[f"mixer{i}_tube_od"].value = mixer_config.get("OD", "")
                self.widgets[f"mixer{i}_tube_material"].value = mixer_config.get(
                    "material", ""
                )

    def _prefill_coils(self, config: Dict[str, Any]) -> None:
        """Helper method to prefill coil widgets"""
        coils = config.get("coils", [])
        num_coils = self.widgets["component_counts"]["coils"]
        coil_letters = ["a", "x", "b", "y"][:num_coils]  # Get only needed letters
        for i, letter in enumerate(coil_letters):
            if i < len(coils):
                self.widgets[f"coil_{letter}"].value = coils[i].get("length", "")
