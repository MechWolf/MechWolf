import json
"""
ComponentApp class handles the creation and management of components for a chemical apparatus setup.
Attributes:
    pumps (List[HarvardSyringePump]): List of syringe pumps used in the setup.
    data_manager (DataManager): Manages the data related to the apparatus configuration.
    data (Dict[str, Any]): Dictionary to store the apparatus data.
    setup_complete (bool): Flag to indicate if the setup is complete.
    existing_config (Optional[Dict[str, Any]]): Existing configuration loaded from the JSON file.
    widget_manager (WidgetManager): Manages the widgets for user input.
Methods:
    create_widgets() -> None:
        Creates and displays widgets for user input with three input vessels and one product vessel.
    create_setup(b: Any) -> None:
        Processes form submission and creates the setup.
    _process_inputs() -> bool:
        Processes and validates all inputs from the widgets.
    _prepare_data(values: Dict[str, Any]) -> None:
        Prepares the data dictionary from widget values.
    _validate_and_process() -> None:
        Validates and processes all inputs.
    _validate_dimensions() -> None:
        Validates all dimensions of the tubes and coils.
    _save_config() -> None:
        Creates and saves the apparatus configuration to a JSON file.
"""
"""
ApparatusCreator class facilitates the creation of a chemical apparatus using syringe pumps.
Attributes:
    pumps (Tuple[HarvardSyringePump, ...]): Tuple of syringe pumps used in the setup.
    json_file (str): Path to the JSON file where the configuration is saved.
    pump_type (str): Type of the pump, either 'single-channel' or 'dual-channel'.
Methods:
    _determine_pump_type() -> str:
        Determines the pump type based on the first pump in the list.
    create_apparatus() -> mw.Apparatus:
        Creates and configures the apparatus.
    _process_events() -> None:
        Processes IPython events to handle widget interactions.
    _build_apparatus() -> mw.Apparatus:
        Builds the apparatus from the saved configuration with three input vessels.
    _load_config() -> Dict[str, Any]:
        Loads the configuration from the JSON file.
    _make_tube(tube_config: Dict[str, Any], length: float) -> mw.Tube:
        Creates a tube with the given configuration and length.
"""
from typing import List, Dict, Any, Optional, Tuple
from IPython.display import clear_output
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from .FlowSetupUtils import parse_tube_dimension, parse_numeric_foot, check_required_fields
from .error_handler import ErrorHandler
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
        """Create and display widgets with three input vessels"""
        self.widgets = self.widget_manager.create_all_widgets(
            num_vessels=4,  # 3 input vessels + 1 product vessel
            num_tubes=1,
            num_coils=2,
            num_mixers=1,
        )

        if self.existing_config:
            self.widget_manager.prefill_values(self.existing_config)

        self.widget_container = self.widget_manager.widget_container

    def create_setup(self, b: Any) -> None:
        """Process form submission and create setup"""
        try:
            if self._process_inputs():
                self.widget_container.close()
                self.setup_complete = True
                clear_output()
                print("Configuration saved successfully!")
        except Exception as e:
            print(f"Error: {str(e)}")

    def _process_inputs(self) -> bool:
        """Process and validate all inputs"""
        widget_values = self.widget_manager.get_widget_values()
        self._prepare_data(widget_values)

        # Check for missing required fields
        missing_fields = check_required_fields(self.data)
        if missing_fields:
            print(
                f"Error: Please fill in these required fields: {', '.join(missing_fields)}"
            )
            self.setup_complete = False
            return False

        try:
            self._validate_and_process()
            self._save_config()
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            self.setup_complete = False
            return False

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
        }

    def _validate_and_process(self) -> None:
        """Validate and process all inputs"""
        # Process and validate tubes
        self.data.update(
            {
                "reaction_tube_ID": parse_tube_dimension(
                    self.data["reaction_tube_id_raw"]
                ),
                "reaction_tube_OD": parse_tube_dimension(
                    self.data["reaction_tube_od_raw"]
                ),
                "coil_a_length": parse_numeric_foot(self.data["coil_a_raw"]),
                "coil_x_length": parse_numeric_foot(self.data["coil_x_raw"]),
            }
        )

        # Validate mixer if used
        if self.data["using_mixer"]:
            self.data.update(
                {
                    "mixer_tube_ID": parse_tube_dimension(
                        self.data["mixer_tube_id_raw"]
                    ),
                    "mixer_tube_OD": parse_tube_dimension(
                        self.data["mixer_tube_od_raw"]
                    ),
                }
            )

        # Validate dimensions
        self._validate_dimensions()

    def _validate_dimensions(self) -> None:
        """Validate all dimensions"""
        tube_data = {
            "reaction_tubes": [
                (self.data["reaction_tube_ID"], self.data["reaction_tube_OD"])
            ]
        }

        if self.data["using_mixer"]:
            tube_data["mixer_tubes"] = [
                (self.data["mixer_tube_ID"], self.data["mixer_tube_OD"])
            ]

        ErrorHandler.validate_tube_dimensions(tube_data)
        ErrorHandler.validate_coil_lengths(
            [self.data["coil_a_length"], self.data["coil_x_length"]]
        )

    def _save_config(self) -> None:
        """Create and save apparatus configuration"""
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
            ],
            "using_mixer": self.data["using_mixer"],
        }

        if self.data["using_mixer"]:
            config["tubes"]["mixer"] = {
                "ID": self.data["mixer_tube_ID"],
                "OD": self.data["mixer_tube_OD"],
                "material": self.data["mixer_tube_material"],
            }

        self.data_manager.save_config(config)

    # ...rest of ComponentApp methods same as Test3.py...


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
        """Build apparatus from saved configuration with three input vessels"""
        config = self._load_config()
        A = mw.Apparatus(config["apparatus_name"])

        # Create vessels - now handling 3 input vessels
        vessels = [
            mw.Vessel(v["description"], name=v["name"]) for v in config["vessels"]
        ]
        vessel1, vessel2, vessel3, product_vessel = vessels

        # Create tubes and components
        coil_a = self._make_tube(
            config["tubes"]["reaction"], config["coils"][0]["length"]
        )
        coil_x = self._make_tube(
            config["tubes"]["reaction"], config["coils"][1]["length"]
        )
        T1 = mw.TMixer(name=coil_x)

        # Add pump connections based on type
        if self.pump_type == "single-channel":
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[1], vessel2, coil_a)
            A.add(self.pumps[2], vessel3, coil_a)
        else:  # dual-channel
            A.add(self.pumps[0], vessel1, coil_a)
            A.add(self.pumps[0], vessel2, coil_a)
            A.add(self.pumps[1], vessel3, coil_a)

        # Add mixer connections
        A.add(vessel1, T1, coil_a)
        A.add(vessel2, T1, coil_a)
        A.add(vessel3, T1, coil_a)
        A.add(T1, product_vessel, coil_x)

        return A

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        with open(self.json_file, "r") as f:
            data = json.load(f)
        if "apparatus_config" not in data:
            raise ValueError("No apparatus configuration found")
        return data["apparatus_config"]

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
