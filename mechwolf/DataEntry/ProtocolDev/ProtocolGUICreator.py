"""
This module provides a graphical user interface (GUI) for configuring pump protocols in a Jupyter notebook environment.
Classes:
    PumpConfig: A dataclass representing the configuration of a pump.
    ProtocolGUI: A class for creating and managing the GUI for pump protocol configuration.
PumpConfig:
    Attributes:
        flow_rate (float): The flow rate of the pump in mL/min.
        volume (float): The volume to be pumped in mL.
        delay (float): The delay before the pump starts in seconds.
        pump (mw.components.ActiveComponent): The pump component.
        vessel (mw.Vessel): The vessel associated with the pump.
ProtocolGUI:
    Attributes:
        pump_vessel_mapping (List[Dict[str, Any]]): A list of dictionaries mapping pumps to vessels.
        json_file (Optional[str]): The path to the JSON file for saving/loading protocol configurations.
        configs (List[PumpConfig]): A list of PumpConfig objects representing the current configuration.
        setup_complete (bool): A flag indicating whether the setup is complete.
        temp_entries (List[Dict[str, Any]]): A temporary list of pump entries.
        current_mapping_index (int): The current index in the pump-vessel mapping.
        data_manager (Optional[ProtocolDataManager]): An optional data manager for handling protocol data.
        full_config (Optional[Dict[str, Any]]): The full configuration loaded from the JSON file.
        existing_config (Optional[Dict[str, Any]]): The existing protocol configuration loaded from the JSON file.
        save_setup_button (widgets.Button): A button for saving the protocol configuration.
        form_container (widgets.VBox): A container for the form elements.
        entries_display (widgets.VBox): A container for displaying pump entries.
        main_container (widgets.HBox): The main container for the GUI.
Methods:
        create_widgets(): Creates and displays the widgets for the GUI.
        initialize_entries(): Initializes the entries list or loads from existing configuration.
        show_next_pump_form(): Displays the form for the next unmapped pump-vessel pair.
        _format_time(seconds: float) -> str: Formats seconds into minutes and seconds.
        pump_entry_window(b: Optional[widgets.Button], entry: Optional[Dict[str, Any]] = None): Displays the form for a pump entry.
        update_entries_display(): Updates the display of pump entries.
        delete_entry(entry: Dict[str, Any]): Deletes an entry and shows an empty form for that position.
        display_main_container(): Re-displays the main container.
        _get_vessels_for_pump(pump_index: int) -> List[str]: Helper method to get all vessels connected to a pump.
        save_protocol(b: Optional[widgets.Button]): Saves the protocol configuration to a JSON file and displays a summary.
"""
import ipywidgets as widgets
from IPython.display import display, clear_output
import mechwolf as mw
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .protocol_data_manager import ProtocolDataManager


@dataclass
class PumpConfig:
    flow_rate: float
    volume: float
    delay: float
    pump: mw.components.ActiveComponent
    vessel: mw.Vessel  # Add vessel to config


class ProtocolGUI:
    def __init__(
        self, pump_vessel_mapping: List[Dict[str, Any]], json_file: Optional[str] = None
    ) -> None:
        self.pump_vessel_mapping = pump_vessel_mapping
        self.configs: List[PumpConfig] = []
        self.setup_complete = False
        self.temp_entries: List[Dict[str, Any]] = []
        self.current_mapping_index = 0
        self.data_manager = ProtocolDataManager(json_file) if json_file else None

        # Load full configuration including apparatus config
        self.full_config = (
            self.data_manager.load_full_config() if self.data_manager else None
        )
        # Load protocol config separately
        self.existing_config = (
            self.data_manager.load_protocol_config() if self.data_manager else None
        )

        self.create_widgets()

    def create_widgets(self) -> None:
        # Left side: Save button and form area
        self.save_setup_button = widgets.Button(
            description="Save Protocol",
            button_style="primary",
            layout=widgets.Layout(width="150px", margin="0 0 20px 0"),
        )
        self.save_setup_button.on_click(self.save_protocol)

        # Create form container with adjusted width
        self.form_container = widgets.VBox(
            [], layout=widgets.Layout(width="100%", padding="10px", margin="0 20px 0 0")
        )

        left_container = widgets.VBox(
            [self.save_setup_button, self.form_container],
            layout=widgets.Layout(width="40%", align_items="flex-start"),
        )

        # Right side: Pump entries display with reduced width
        self.entries_display = widgets.VBox(
            [], layout=widgets.Layout(width="100%", padding="10px")
        )

        right_container = widgets.VBox(
            [widgets.HTML("<h3>Pump Entries</h3>"), self.entries_display],
            layout=widgets.Layout(width="60%", margin="0 0 0 20px"),
        )

        # Main container for better compatibility across versions
        self.main_container = widgets.VBox([
            widgets.HBox(
                [left_container, right_container], 
                layout=widgets.Layout(width="100%")
            )
        ])

        display(self.main_container)

        # Load existing entries or create new ones for all pumps
        if self.existing_config and "pump_entries" in self.existing_config:
            # Convert existing entries to our format
            for entry in self.existing_config["pump_entries"]:
                mapping = self.pump_vessel_mapping[entry["mapping_index"]]
                new_entry = {
                    "flow_rate": entry["flow_rate"],
                    "volume": entry["volume"],
                    "delay": entry["delay"],
                    "mapping_index": entry["mapping_index"],
                    "pump": mapping["pump"],
                    "vessel": mapping["vessel"],
                    "pump_index": mapping["pump_index"],
                }
                self.temp_entries.append(new_entry)
        else:
            # Create default entries for all pumps
            for i, mapping in enumerate(self.pump_vessel_mapping):
                new_entry = {
                    "flow_rate": 0.0,
                    "volume": 0.0,
                    "delay": 0.0,
                    "mapping_index": i,
                    "pump": mapping["pump"],
                    "vessel": mapping["vessel"],
                    "pump_index": mapping["pump_index"],
                }
                self.temp_entries.append(new_entry)

        self.current_mapping_index = len(self.temp_entries)
        self.update_entries_display()

    def initialize_entries(self) -> None:
        """Initialize empty entries list or load from existing config"""
        if (self.existing_config and "pump_entries" in self.existing_config):
            # Load existing entries
            for entry in self.existing_config["pump_entries"]:
                self.temp_entries.append(entry)
        else:
            # Just create empty entries list
            self.temp_entries = []

        # Show initial empty list
        self.update_entries_display()

    def show_next_pump_form(self) -> None:
        """Show form for next unmapped pump-vessel pair"""
        if self.current_mapping_index < len(self.pump_vessel_mapping):
            self.pump_entry_window(None)
        else:
            print(
                "All pumps have been configured. Use Edit buttons to modify existing entries."
            )

    def _format_time(self, seconds: float) -> str:
        """Format seconds into minutes and seconds"""
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        if minutes > 0:
            return f"{minutes} min {remaining_seconds:.1f} s"
        return f"{remaining_seconds:.1f} s"

    def pump_entry_window(
        self, b: Optional[widgets.Button], entry: Optional[Dict[str, Any]] = None
    ) -> None:
        # Hide the save protocol button when form is active
        self.save_setup_button.layout.display = "none"

        mapping_index = (
            entry["mapping_index"] if entry is not None else self.current_mapping_index
        )
        mapping = self.pump_vessel_mapping[mapping_index]

        # Create input fields with improved styling
        flow_rate = widgets.BoundedFloatText(
            value=entry["flow_rate"] if entry is not None else 0.0,
            min=0.000001,  # Prevent divide by zero
            max=1000.0,  # Reasonable upper limit
            description="Flow Rate (mL/min):",
            layout=widgets.Layout(width="100%"),
        )

        volume = widgets.BoundedFloatText(
            value=entry["volume"] if entry is not None else 0.0,
            min=0.000001,  # Minimum volume
            max=1000.0,  # Reasonable upper limit
            description="Volume (mL):",
            layout=widgets.Layout(width="100%"),
        )

        delay = widgets.BoundedFloatText(
            value=entry["delay"] if entry is not None else 0.0,
            min=0.0,  # Allow zero delay
            max=86400.0,  # 24 hours in seconds
            description="Delay (s):",
            layout=widgets.Layout(width="100%"),
        )

        pump_info = widgets.HTML(
            value=(
                f"<h3>Current Pump-Vessel Pair ({mapping_index + 1}/{len(self.pump_vessel_mapping)})</h3>"
                f"<p><b>Pump {mapping['pump_index']} → {mapping['vessel'].name}</b></p>"
            ),
            layout=widgets.Layout(width="100%", margin="0 0 20px 0"),
        )

        # Create input fields with more space
        input_style = {"description_width": "150px"}  # Wider label

        flow_rate = widgets.BoundedFloatText(
            value=entry["flow_rate"] if entry is not None else 0.0,
            min=-1000.0,  # Allow negative flow rates for backward operation
            max=1000.0,  # Reasonable upper limit
            description="Flow Rate (mL/min):",
            style=input_style,
            layout=widgets.Layout(width="300px", margin="5px 0"),  # Reduced width
        )

        volume = widgets.BoundedFloatText(
            value=entry["volume"] if entry is not None else 0.0,
            min=0.000001,  # Minimum volume
            max=1000.0,  # Reasonable upper limit
            description="Volume (mL):",
            style=input_style,
            layout=widgets.Layout(width="300px", margin="5px 0"),
        )

        delay = widgets.BoundedFloatText(
            value=entry["delay"] if entry is not None else 0.0,
            min=0.0,  # Allow zero delay
            max=86400.0,  # 24 hours in seconds
            description="Delay (s):",
            style=input_style,
            layout=widgets.Layout(width="300px", margin="5px 0"),
        )

        active_time_display = widgets.HTML(
            value="Active Time: 0 seconds",
            layout=widgets.Layout(width="300px", margin="15px 0"),  # Added more margin
        )

        def update_active_time(*args: Any) -> None:
            if flow_rate.value and volume.value:
                # Use absolute value of flow rate for time calculation
                active_time = (volume.value / abs(flow_rate.value)) * 60
                formatted_time = self._format_time(active_time)
                active_time_display.value = f"Active Time: {formatted_time}"

        flow_rate.observe(update_active_time, "value")
        volume.observe(update_active_time, "value")

        save_btn = widgets.Button(
            description="Save Entry",
            button_style="success",
            layout=widgets.Layout(width="150px", margin="15px 0"),  # Added margin
        )

        def save_entry(btn: widgets.Button) -> None:
            new_entry = {
                "flow_rate": flow_rate.value,
                "volume": volume.value,
                "delay": delay.value,
                "mapping_index": mapping_index,
                "pump": mapping["pump"],
                "vessel": mapping["vessel"],
                "active_time": active_time_display.value,
                "pump_index": mapping["pump_index"],
            }

            if entry:
                index = self.temp_entries.index(entry)
                self.temp_entries[index] = new_entry
            else:
                self.temp_entries.append(new_entry)

            self.update_entries_display()
            # Clear the form
            self.form_container.children = ()
            # Show save protocol button
            self.save_setup_button.layout.display = "block"

        save_btn.on_click(save_entry)

        # Stack form elements vertically with more space for better compatibility
        form = widgets.VBox(
            [
                pump_info,
                flow_rate,
                volume,
                delay,
                active_time_display,
                widgets.Box(
                    [save_btn],
                    layout=widgets.Layout(display="flex", justify_content="flex-start"),
                ),  # Aligned left
            ],
            layout=widgets.Layout(
                padding="20px", max_width="800px"
            ),  # Added max-width and more padding
        )

        # Update the form container
        self.form_container.children = (form,)

    def update_entries_display(self) -> None:
        self.save_setup_button.layout.display = "block"
        entries = []

        # Group entries by pump index
        pump_entries: Dict[int, Dict[str, Any]] = {}
        for entry in self.temp_entries:
            pump_idx = entry["pump_index"]
            if pump_idx not in pump_entries:
                connected_vessels = self._get_vessels_for_pump(pump_idx)
                vessels_str = (
                    ", ".join(connected_vessels)
                    if connected_vessels
                    else entry["vessel"].name
                )

                pump_entries[pump_idx] = {
                    "flow_rate": entry["flow_rate"],
                    "volume": entry["volume"],
                    "delay": entry["delay"],
                    "vessels": vessels_str,
                    "mapping_index": entry["mapping_index"],
                    "entry": entry,
                }

        # Create display entries
        for pump_idx, details in sorted(pump_entries.items()):
            # Include direction indication in the display
            direction = " (backward)" if details["flow_rate"] < 0 else ""
            flow_rate_display = abs(details["flow_rate"])  # Show absolute value
            
            label = widgets.HTML(
                value=(
                    f"<div style='font-size: 14px; padding: 5px;'>"
                    f"Pump {pump_idx} → {details['vessels']}: "
                    f"{flow_rate_display} mL/min{direction}, {details['volume']} mL, {details['delay']}s delay</div>"
                ),
                layout=widgets.Layout(width="100%"),
            )

            edit_btn = widgets.Button(
                description="Edit",
                button_style="info",
                layout=widgets.Layout(width="80px"),
            )

            edit_btn.on_click(
                lambda b, e=details["entry"]: self.pump_entry_window(b, entry=e)
            )

            entry_box = widgets.HBox(
                [label, edit_btn],
                layout=widgets.Layout(margin="5px 0", align_items="center"),
            )
            entries.append(entry_box)

        # Add header text if no entries yet
        if not entries:
            entries.append(widgets.HTML("<i>No pump configurations yet</i>"))

        self.entries_display.children = tuple(entries)

    def delete_entry(self, entry: Dict[str, Any]) -> None:
        """Delete an entry and show empty form for that position"""
        if entry in self.temp_entries:
            # Store the mapping index before deleting
            mapping_index = entry["mapping_index"]
            self.temp_entries.remove(entry)
            self.update_entries_display()

            # Show empty form for this position, but don't auto-progress
            self.current_mapping_index = mapping_index
            # Clear output before showing new form - use wait=True for compatibility
            clear_output(wait=True)
            self.display_main_container()
            self.pump_entry_window(None)

    def display_main_container(self) -> None:
        """Re-display the main container"""
        display(self.main_container)

    def _get_vessels_for_pump(self, pump_index: int) -> List[str]:
        """Helper method to get all vessels connected to a pump"""
        try:
            if not self.full_config:
                return []

            # Get vessels from the apparatus_config section
            vessels = []
            if (
                "apparatus_config" in self.full_config
                and "vessels" in self.full_config["apparatus_config"]
            ):
                for vessel in self.full_config["apparatus_config"]["vessels"]:
                    if str(vessel["pump_number"]) == str(pump_index):
                        vessels.append(vessel["vessel_name"])

            return sorted(vessels)
        except Exception as e:
            return []

    def save_protocol(self, b: Optional[widgets.Button]) -> None:
        if self.data_manager:
            protocol_config = {
                "name": "",  # Add empty default name
                "description": "",  # Add empty default description
                "pump_entries": [],
            }

            for entry in self.temp_entries:
                serialized_entry = {
                    "flow_rate": entry["flow_rate"],
                    "volume": entry["volume"],
                    "delay": entry["delay"],
                    "pump_index": entry["pump_index"],
                    "vessel_name": entry["vessel"].name,
                    "mapping_index": entry["mapping_index"],
                }
                protocol_config["pump_entries"].append(serialized_entry)

            self.data_manager.save_protocol_config(protocol_config)

        self.configs = []
        for entry in self.temp_entries:
            config = PumpConfig(
                flow_rate=entry["flow_rate"],
                volume=entry["volume"],
                delay=entry["delay"],
                pump=entry["pump"],
                vessel=entry["vessel"],
            )
            self.configs.append(config)

        self.setup_complete = True
        self.main_container.close()
        clear_output(wait=True)  # Use wait parameter for compatibility

        # Center the header
        print("\n" + "=" * 50)
        print("Protocol Configuration Summary".center(50))
        print("=" * 50 + "\n")

        # Group entries by pump index and collect all vessels
        pump_entries: Dict[int, Dict[str, Any]] = {}
        try:
            for entry in self.temp_entries:
                pump_idx = entry["pump_index"]
                if pump_idx not in pump_entries:
                    connected_vessels = self._get_vessels_for_pump(pump_idx)

                    pump_entries[pump_idx] = {
                        "flow_rate": entry["flow_rate"],
                        "volume": entry["volume"],
                        "delay": entry["delay"],
                        "vessels": connected_vessels
                        if connected_vessels
                        else [entry["vessel"].name],
                    }
        except Exception as e:
            print(f"Error processing pump entries: {str(e)}")

        # Print each pump's configuration
        for pump_idx, details in sorted(pump_entries.items()):
            vessels_str = ", ".join(details["vessels"])
            direction = " (backward)" if details["flow_rate"] < 0 else ""
            flow_display = abs(details["flow_rate"])
            
            pump_info = f"Pump {pump_idx} → {vessels_str}"
            flow_info = f"Flow Rate: {flow_display} mL/min{direction}"
            volume_info = f"Volume: {details['volume']} mL"
            delay_info = f"Delay: {details['delay']} s"
            
            # Use absolute value of flow rate for time calculation
            active_time = (details["volume"] / abs(details["flow_rate"])) * 60
            time_info = f"Active Time: {self._format_time(active_time)}"

            print(f"     {pump_info}")
            print(f"     {flow_info}")
            print(f"     {volume_info}")
            print(f"     {delay_info}")
            print(f"     {time_info}")
            print("-" * 50)

        print(f"\nTotal entries: {len(self.configs)}".center(50))
