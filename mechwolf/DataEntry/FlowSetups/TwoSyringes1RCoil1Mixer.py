import json

"""
This module defines classes and methods for creating and managing a chemical apparatus setup using MechWolf and IPython widgets.
Classes:
    ComponentApp: Manages the creation and configuration of apparatus components using widgets.
    ApparatusCreator: Facilitates the creation of an apparatus from a given configuration.
ComponentApp:
    __init__(self, pumps: List[HarvardSyringePump], json_file: str) -> None:
        Initializes the ComponentApp with the given pumps and JSON configuration file.
    create_widgets(self) -> None:
        Creates and displays widgets for configuring the apparatus components.
    create_setup(self, b: Any) -> None:
        Gathers inputs, validates them, processes tube dimensions and coil lengths, and saves the apparatus configuration.
    _gather_inputs(self) -> None:
        Gathers all widget values using the widget manager.
    _process_tube_dimensions(self) -> None:
        Processes and validates the dimensions of the reaction and mixer tubes.
    _process_coil_lengths(self) -> None:
        Processes and validates the lengths of the coils.
    _create_apparatus_config(self) -> Dict[str, Any]:
        Creates and returns the apparatus configuration dictionary.
ApparatusCreator:
    __init__(self, *pumps: HarvardSyringePump, data_file: Optional[str] = None) -> None:
        Initializes the ApparatusCreator with the given pumps and optional data file.
    determine_pump_type(self) -> str:
        Determines and returns the type of pump (single-channel or dual-channel).
    create_apparatus(self) -> mw.Apparatus:
        Creates and returns an apparatus based on the saved configuration.
"""
from IPython.display import clear_output
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from typing import List, Dict, Any, Optional, Tuple
from .FlowSetupUtils import parse_tube_dimension, parse_numeric_foot
from .error_handler import ErrorHandler, ValidationError
from .data_manager import DataManager
from .widget_manager import WidgetManager


class ComponentApp:
    def __init__(self, pumps: List[HarvardSyringePump], json_file: str) -> None:
        self.pumps: List[HarvardSyringePump] = pumps
        self.data_manager: DataManager = DataManager(json_file)
        self.data: Dict[str, Any] = {}
        self.setup_complete: bool = False
        self.existing_config: Optional[Dict[str, Any]] = self.data_manager.load_config()
        self.widget_manager: WidgetManager = WidgetManager(self)

    def create_widgets(self) -> None:
        """Create widgets using the widget manager"""
        self.widgets = self.widget_manager.create_all_widgets(
            num_vessels=3,  # 2 vessels + 1 product vessel
            num_tubes=1,
            num_coils=2,
            num_mixers=1,
        )

        if self.existing_config:
            self.widget_manager.prefill_values(self.existing_config)

        # Store widget_container reference
        self.widget_container = self.widget_manager.widget_container

    def create_setup(self, b: Any) -> None:
        try:
            # Gather all inputs
            self._gather_inputs()

            # Rest of validation and processing
            ErrorHandler.validate_mixer_inputs(self.data)
            self._process_tube_dimensions()
            self._process_coil_lengths()

            # Create and save apparatus configuration
            apparatus_config = self._create_apparatus_config()
            self.data_manager.save_config(apparatus_config)

            self.widget_container.close()
            self.setup_complete = True
            clear_output()
            print("Configuration saved successfully!")

        except ValidationError as e:
            print(f"Validation Error: {str(e)}")
        except Exception as e:
            print(f"Error: {str(e)}")

    def _gather_inputs(self) -> None:
        """Gather all widget values using widget manager"""
        widget_values = self.widget_manager.get_widget_values()

        self.data = {
            "apparatus_name": widget_values["apparatus_name"],
            "vessel1_name": widget_values["vessel1_name"],
            "vessel1_desc": widget_values["vessel1_desc"],
            "vessel2_name": widget_values["vessel2_name"],
            "vessel2_desc": widget_values["vessel2_desc"],
            "product_vessel_name": widget_values["product_vessel_name"],
            "product_vessel_desc": widget_values["product_vessel_desc"],
            "reaction_tube_id_raw": widget_values["reaction_tube1_id"],
            "reaction_tube_od_raw": widget_values["reaction_tube1_od"],
            "reaction_tube_material": widget_values["reaction_tube1_material"],
            "using_mixer": widget_values["using_mixer"],
            "mixer_tube_id_raw": widget_values["mixer1_tube_id"],
            "mixer_tube_od_raw": widget_values["mixer1_tube_od"],
            "mixer_tube_material": widget_values["mixer1_tube_material"],
            "coil_a_raw": widget_values["coil_a"],
            "coil_x_raw": widget_values["coil_x"],
        }

    def _process_tube_dimensions(self) -> None:
        self.data["reaction_tube_ID"] = parse_tube_dimension(
            self.data["reaction_tube_id_raw"]
        )
        self.data["reaction_tube_OD"] = parse_tube_dimension(
            self.data["reaction_tube_od_raw"]
        )

        tube_data = {
            "reaction_tubes": [
                (self.data["reaction_tube_ID"], self.data["reaction_tube_OD"])
            ]
        }

        if self.data["using_mixer"]:
            self.data["mixer_tube_ID"] = parse_tube_dimension(
                self.data["mixer_tube_id_raw"]
            )
            self.data["mixer_tube_OD"] = parse_tube_dimension(
                self.data["mixer_tube_od_raw"]
            )
            tube_data["mixer_tubes"] = [
                (self.data["mixer_tube_ID"], self.data["mixer_tube_OD"])
            ]

        ErrorHandler.validate_tube_dimensions(tube_data)

    def _process_coil_lengths(self) -> None:
        self.data["coil_a_length"] = parse_numeric_foot(self.data["coil_a_raw"])
        self.data["coil_x_length"] = parse_numeric_foot(self.data["coil_x_raw"])

        # Pass coil lengths as a list instead of separate arguments
        coil_lengths = [self.data["coil_a_length"], self.data["coil_x_length"]]
        ErrorHandler.validate_coil_lengths(coil_lengths)

    def _create_apparatus_config(self) -> Dict[str, Any]:
        config = {
            "apparatus_name": self.data["apparatus_name"],
            "vessels": [
                {
                    "name": self.data["vessel1_name"],
                    "description": self.data["vessel1_desc"],
                },
                {
                    "name": self.data["vessel2_name"],
                    "description": self.data["vessel2_desc"],
                },
                {
                    "name": self.data["product_vessel_name"],
                    "description": self.data["product_vessel_desc"],
                },
            ],
            "tubes": {
                "reaction": {
                    "ID": self.data["reaction_tube_ID"],
                    "OD": self.data["reaction_tube_OD"],
                    "material": self.data["reaction_tube_material"],
                }
            },
            "coils": [
                {"length": self.data["coil_a_length"]},
                {"length": self.data["coil_x_length"]},
            ],
            "using_mixer": self.data["using_mixer"],
        }

        # Add mixer tube details if using mixer
        if self.data["using_mixer"]:
            config["tubes"]["mixer"] = {
                "ID": self.data["mixer_tube_ID"],
                "OD": self.data["mixer_tube_OD"],
                "material": self.data["mixer_tube_material"],
            }

        return config


class ApparatusCreator:
    def __init__(
        self, *pumps: HarvardSyringePump, data_file: Optional[str] = None
    ) -> None:
        self.pumps: Tuple[HarvardSyringePump, ...] = pumps
        self.json_file: str = data_file if data_file else "apparatus_config.json"
        self.pump_type: str = self.determine_pump_type()

    def determine_pump_type(self) -> str:
        for pump in self.pumps:
            if isinstance(pump, HarvardSyringePump):
                return "dual-channel"
        return "single-channel"

    def create_apparatus(self) -> mw.Apparatus:
        import time
        from IPython import get_ipython
        import asyncio

        # Create and display widgets
        app = ComponentApp(self.pumps, self.json_file)
        app.create_widgets()

        # Block until setup is complete
        while not app.setup_complete:
            time.sleep(0.1)  # Small delay
            # Force IPython to process events properly
            if get_ipython():
                loop = asyncio.get_event_loop()
                loop.run_until_complete(get_ipython().kernel.do_one_iteration())

        # Now read the saved configuration and create apparatus
        with open(self.json_file, "r") as f:
            data = json.load(f)

        if "apparatus_config" not in data:
            raise ValueError("No apparatus configuration found")

        config = data["apparatus_config"]
        print(f"Using configuration: {config['apparatus_name']}")

        # Create apparatus from config
        A = mw.Apparatus(config["apparatus_name"])

        # Create vessels
        vessels = [
            mw.Vessel(v["description"], name=v["name"]) for v in config["vessels"]
        ]
        vessel1, vessel2, product_vessel = vessels

        # Create tubes function
        def make_tube(
            tube_config: Dict[str, Any], length: Optional[float] = None
        ) -> mw.Tube:
            return mw.Tube(
                length=length or "0 in",
                ID=tube_config["ID"],
                OD=tube_config["OD"],
                material=tube_config["material"],
            )

        # Create tubes and coils with updated names
        reaction_tube = lambda length: make_tube(config["tubes"]["reaction"], length)
        if config["using_mixer"]:
            mixer_tube = lambda length: make_tube(config["tubes"]["mixer"], length)

        coil_a = reaction_tube(config["coils"][0]["length"])
        coil_x = reaction_tube(config["coils"][1]["length"])

        # Create T Mixer component (matching main program)
        def Tmixer(name: str) -> mw.TMixer:
            """Returns a TMixer with the given name."""
            return mw.TMixer(name=name)

        T1 = Tmixer(coil_x)
        # Build apparatus with the pumps (matching main program order)
        A = mw.Apparatus(config["apparatus_name"])

        # Add pump connections first
        if self.pump_type == "single-channel":
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[1], vessel2, coil_a)
        elif self.pump_type == "dual-channel":
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[0], vessel2, coil_a)

        # Add mixer and coil connections in same order as main program
        A.add(vessel1, T1, coil_a)
        A.add(vessel2, T1, coil_a)
        A.add(T1, product_vessel, coil_x)

        return A


if __name__ == "__main__":
    pump_1 = HarvardSyringePump()
    pump_2 = HarvardSyringePump()
    creator = ApparatusCreator(pump_1, pump_2, data_file="apparatus_config.json")
    creator.create_apparatus()
