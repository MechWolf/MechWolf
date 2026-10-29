import json
"""
ComponentApp class handles the creation and management of widgets for configuring a multi-component apparatus setup.
Attributes:
    pumps (List[HarvardSyringePump]): List of syringe pumps used in the setup.
    data_manager (DataManager): Manages loading and saving of configuration data.
    data (Dict[str, Any]): Dictionary to store configuration data.
    setup_complete (bool): Flag indicating if the setup is complete.
    existing_config (Optional[Dict[str, Any]]): Existing configuration data if available.
    widget_manager (WidgetManager): Manages the creation and handling of widgets.
Methods:
    create_widgets(): Creates widgets for the apparatus setup using the widget manager.
    create_setup(b: Any): Gathers inputs, validates, processes, and saves the apparatus configuration.
    _gather_inputs(): Gathers all widget values using the widget manager.
    _prepare_data(values: Dict[str, Any]): Prepares data dictionary from widget values.
    _process_tube_dimensions(): Processes and validates tube dimensions.
    _process_coil_lengths(): Processes and validates coil lengths.
    _create_apparatus_config() -> Dict[str, Any]: Creates and returns the apparatus configuration dictionary.
"""
"""
ApparatusCreator class handles the creation and configuration of an apparatus with multiple syringe pumps.
Attributes:
    pumps (Tuple[HarvardSyringePump, ...]): Tuple of syringe pumps used in the setup.
    json_file (str): Path to the JSON file for saving/loading configuration.
    pump_type (str): Type of pump (single-channel or dual-channel).
Methods:
    _determine_pump_type() -> str: Determines the pump type based on the first pump.
    create_apparatus() -> mw.Apparatus: Creates and configures the apparatus.
    _process_events(): Processes IPython events.
    _build_apparatus() -> mw.Apparatus: Builds the apparatus from the saved configuration.
    _load_config() -> Dict[str, Any]: Loads configuration from the JSON file.
    _make_tube(tube_config: Dict[str, Any], length: float) -> mw.Tube: Creates a tube with the given configuration.
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
            num_vessels=4,  # 3 vessels + 1 product vessel
            num_tubes=1,
            num_coils=4,  # Four coils: a, x, b, y
            num_mixers=2,  # Two mixers for this setup
        )

        if self.existing_config:
            self.widget_manager.prefill_values(self.existing_config)

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
            "vessel3_name": widget_values["vessel3_name"],
            "vessel3_desc": widget_values["vessel3_desc"],
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
            "coil_b_raw": widget_values["coil_b"],
            "coil_y_raw": widget_values["coil_y"],
        }

    def _prepare_data(self, values: Dict[str, Any]) -> None:
        """Prepare data dictionary from widget values"""
        self.data = {
            "apparatus_name": values["apparatus_name"],
            "vessel1_name": values["vessel1_name"],
            "vessel1_desc": values["vessel1_desc"],
            "vessel2_name": values["vessel2_name"],
            "vessel2_desc": values["vessel2_desc"],
            "vessel3_name": values["vessel3_name"],
            "vessel3_desc": values["vessel3_desc"],
            "product_vessel_name": values["product_vessel_name"],
            "product_vessel_desc": values["product_vessel_desc"],
            "reaction_tube_id_raw": values["reaction_tube1_id"],
            "reaction_tube_od_raw": values["reaction_tube1_od"],
            "reaction_tube_material": values["reaction_tube1_material"],
            "using_mixer": values["using_mixer"],
            "mixer_tube_id_raw": values["mixer1_tube_id"],
            "mixer_tube_od_raw": values["mixer1_tube_od"],
            "mixer_tube_material": values["mixer1_tube_material"],
            "coil_a_raw": values["coil_a"],  # Changed from 'coil_1'
            "coil_x_raw": values["coil_x"],  # Changed from 'coil_2'
            "coil_b_raw": values["coil_b"],  # For the second setup
            "coil_y_raw": values["coil_y"],  # For the second setup
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
        self.data.update(
            {
                "coil_a_length": parse_numeric_foot(self.data["coil_a_raw"]),
                "coil_x_length": parse_numeric_foot(self.data["coil_x_raw"]),
                "coil_b_length": parse_numeric_foot(self.data["coil_b_raw"]),
                "coil_y_length": parse_numeric_foot(self.data["coil_y_raw"]),
            }
        )

        coil_lengths = [
            self.data["coil_a_length"],
            self.data["coil_x_length"],
            self.data["coil_b_length"],
            self.data["coil_y_length"],
        ]
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
                    "name": self.data["vessel3_name"],
                    "description": self.data["vessel3_desc"],
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
                {"length": self.data["coil_b_length"]},
                {"length": self.data["coil_y_length"]},
            ],
            "using_mixer": self.data["using_mixer"],
        }

        if self.data["using_mixer"]:
            config["tubes"]["mixer"] = {
                "ID": self.data["mixer_tube_ID"],
                "OD": self.data["mixer_tube_OD"],
                "material": self.data["mixer_tube_material"],
            }

        return config


# ...rest of the file remains unchanged...


class ApparatusCreator:
    def __init__(
        self, *pumps: HarvardSyringePump, data_file: Optional[str] = None
    ) -> None:
        self.pumps: Tuple[HarvardSyringePump, ...] = pumps
        self.json_file: str = data_file if data_file else "apparatus_config.json"
        self.pump_type: str = self._determine_pump_type()

    def _determine_pump_type(self) -> str:
        """Determine pump type based on first pump"""
        return (
            "dual-channel"
            if isinstance(self.pumps[0], HarvardSyringePump)
            else "single-channel"
        )

    def create_apparatus(self) -> mw.Apparatus:
        """Create and configure the apparatus"""
        app = ComponentApp(self.pumps, self.json_file)
        app.create_widgets()

        while not app.setup_complete:
            self._process_events()

        return self._build_apparatus()

    def _process_events(self) -> None:
        """Process IPython events"""
        import time
        from IPython import get_ipython
        import asyncio

        time.sleep(0.1)
        if get_ipython():
            loop = asyncio.get_event_loop()
            loop.run_until_complete(get_ipython().kernel.do_one_iteration())

    def _build_apparatus(self) -> mw.Apparatus:
        """Build apparatus from saved configuration with three input vessels and two mixers"""
        config = self._load_config()
        A = mw.Apparatus(config["apparatus_name"])

        # Create vessels
        vessels = [
            mw.Vessel(v["description"], name=v["name"]) for v in config["vessels"]
        ]
        vessel1, vessel2, vessel3, product_vessel = vessels

        # Create tubes and coils
        coil_a = self._make_tube(
            config["tubes"]["reaction"], config["coils"][0]["length"]
        )
        coil_x = self._make_tube(
            config["tubes"]["reaction"], config["coils"][1]["length"]
        )
        coil_b = self._make_tube(
            config["tubes"]["reaction"], config["coils"][2]["length"]
        )
        coil_y = self._make_tube(
            config["tubes"]["reaction"], config["coils"][3]["length"]
        )

        # Create mixers
        T1 = mw.TMixer(name=coil_x)
        T2 = mw.TMixer(name=coil_y)

        # Add pump connections based on type
        if self.pump_type == "single-channel":
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[1], vessel2, coil_a)
            A.add(self.pumps[2], vessel3, coil_b)
        else:  # dual-channel
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[0], vessel2, coil_a)
            A.add(self.pumps[1], vessel3, coil_b)

        # Add mixer and coil connections
        A.add(vessel1, T1, coil_a)
        A.add(vessel2, T1, coil_a)
        A.add(vessel3, T2, coil_b)
        A.add(T1, T2, coil_x)
        A.add(T2, product_vessel, coil_y)

        return A

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
                if "apparatus_config" in data:
                    return data["apparatus_config"]
                raise ValueError("No apparatus configuration found")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading configuration: {str(e)}")

    def _make_tube(self, tube_config: Dict[str, Any], length: float) -> mw.Tube:
        """Create a tube with given configuration"""
        return mw.Tube(
            length=length,
            ID=tube_config["ID"],
            OD=tube_config["OD"],
            material=tube_config["material"],
        )


if __name__ == "__main__":
    pump_1 = HarvardSyringePump()
    pump_2 = HarvardSyringePump()
    pump_3 = HarvardSyringePump()
    creator = ApparatusCreator(
        pump_1, pump_2, pump_3, data_file="apparatus_config.json"
    )
    creator.create_apparatus()
