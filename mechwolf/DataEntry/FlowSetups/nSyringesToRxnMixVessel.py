"""
This module provides a graphical user interface for configuring an apparatus setup using ipywidgets.
Classes:
    ComponentApp: A class to create and manage the GUI for configuring the apparatus.
    ApparatusCreator: A class to create an apparatus based on the configuration provided by the ComponentApp.
ComponentApp:
    __init__(self, pumps: List[HarvardSyringePump], json_file: str) -> None:
        Initializes the ComponentApp with a list of pumps and a JSON file for configuration.
    create_widgets(self) -> None:
        Creates and displays the widgets for the apparatus configuration.
    vessel_window(self, b: widgets.Button, vessel: Optional[Dict[str, Any]] = None) -> None:
        Opens a window to add or edit a vessel configuration.
    update_vessel_display(self) -> None:
        Updates the display of the list of vessels.
    delete_vessel(self, vessel: Dict[str, Any]) -> None:
        Deletes a vessel from the temporary vessel list.
    create_setup(self, b: widgets.Button) -> None:
        Gathers inputs, validates them, and saves the configuration.
    _gather_inputs(self) -> None:
        Gathers inputs from the widgets and stores them in the data dictionary.
    _create_apparatus_config(self) -> Dict[str, Any]:
        Creates the apparatus configuration dictionary from the gathered inputs.
ApparatusCreator:
    __init__(self, *pumps: HarvardSyringePump, data_file: Optional[str] = None) -> None:
        Initializes the ApparatusCreator with a list of pumps and an optional data file.
    create_apparatus(self) -> mw.Apparatus:
        Creates and returns an apparatus based on the configuration provided by the ComponentApp.
"""
import json
import ipywidgets as widgets
from IPython.display import display, clear_output
import mechwolf as mw
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
from typing import Any, Dict, List, Optional
from .FlowSetupUtils import (
    parse_tube_dimension,
    parse_numeric_foot,
    validate_required_fields_with_rmv,
)
from .error_handler import ValidationError
from .data_manager import DataManager


class ComponentApp:
    def __init__(self, pumps: List[HarvardSyringePump], json_file: str) -> None:
        self.pumps: List[HarvardSyringePump] = pumps
        self.data_manager: DataManager = DataManager(json_file)
        self.data: Dict[str, Any] = {}
        self.setup_complete: bool = False
        self.temp_vessels: List[Dict[str, Any]] = []
        self.save_setup_button: Optional[widgets.Button] = None
        self.existing_config: Dict[str, Any] = self.data_manager.load_config()

    def create_widgets(self) -> None:
        apparatus_name_label = widgets.Label("Apparatus Name:")
        self.apparatus_name_widget = widgets.Text(
            value=self.existing_config.get("apparatus_name", "")
            if self.existing_config
            else "",
            layout=widgets.Layout(width="50%"),
        )

        rmv_name_label = widgets.Label("Reaction Mixture Vessel Name:")
        self.product_vessel_name_widget = widgets.Text(
            value=self.existing_config.get("reaction_mixture_vessel", {}).get(
                "name", ""
            )
            if self.existing_config
            else "",
            layout=widgets.Layout(width="50%"),
        )

        rmv_desc_label = widgets.Label("Reaction Mixture Vessel Description:")
        self.product_vessel_desc_widget = widgets.Text(
            value=self.existing_config.get("reaction_mixture_vessel", {}).get(
                "description", ""
            )
            if self.existing_config
            else "",
            layout=widgets.Layout(width="50%"),
        )

        add_vessel_button = widgets.Button(
            description="Add Vessel", button_style="info"
        )
        add_vessel_button.on_click(self.vessel_window)
        self.save_setup_button = widgets.Button(
            description="Save Setup", button_style="success"
        )
        self.save_setup_button.on_click(self.create_setup)

        left_container = widgets.VBox(
            [
                widgets.VBox([apparatus_name_label, self.apparatus_name_widget]),
                widgets.VBox([rmv_name_label, self.product_vessel_name_widget]),
                widgets.VBox([rmv_desc_label, self.product_vessel_desc_widget]),
                add_vessel_button,
                self.save_setup_button,
            ],
            layout=widgets.Layout(width="40%", margin="0 20px 0 0"),
        )

        self.vessel_display = widgets.VBox(
            [], layout=widgets.Layout(width="60%", padding="10px")
        )
        right_container = widgets.VBox(
            [widgets.HTML("<h3>Vessel List</h3>"), self.vessel_display],
            layout=widgets.Layout(width="60%"),
        )

        self.widget_container = widgets.HBox(
            [left_container, right_container], layout=widgets.Layout(width="100%")
        )

        if self.existing_config and "vessels" in self.existing_config:
            self.temp_vessels = self.existing_config["vessels"]
            self.update_vessel_display()

        display(self.widget_container)

    def vessel_window(
        self, b: widgets.Button, vessel: Optional[Dict[str, Any]] = None
    ) -> None:
        if self.save_setup_button:
            self.save_setup_button.layout.visibility = "hidden"

        out = widgets.Output()
        with out:
            vessel_name = widgets.Text(
                value=vessel["vessel_name"] if vessel else "",
                layout=widgets.Layout(width="50%"),
            )
            vessel_desc = widgets.Text(
                value=vessel["vessel_desc"] if vessel else "",
                layout=widgets.Layout(width="50%"),
            )
            pump_dropdown = widgets.Dropdown(
                options=[(f"Pump {i}", str(i)) for i in range(len(self.pumps))],
                value=vessel["pump_number"] if vessel else "0",
                layout=widgets.Layout(width="50%"),
            )
            tube_id = widgets.Text(
                value=vessel["tube_id"] if vessel else "",
                layout=widgets.Layout(width="50%"),
            )
            tube_od = widgets.Text(
                value=vessel["tube_od"] if vessel else "",
                layout=widgets.Layout(width="50%"),
            )
            tube_length = widgets.Text(
                value=vessel["tube_length"] if vessel else "",
                layout=widgets.Layout(width="50%"),
            )
            tube_material = widgets.Text(
                value=vessel["tube_material"] if vessel else "",
                layout=widgets.Layout(width="50%"),
            )
            save_btn = widgets.Button(description="Save Vessel", button_style="success")

            def save_vessel(btn: widgets.Button) -> None:
                new_vessel = {
                    "vessel_name": vessel_name.value,
                    "vessel_desc": vessel_desc.value,
                    "pump_number": pump_dropdown.value,
                    "tube_id": parse_tube_dimension(tube_id.value),
                    "tube_od": parse_tube_dimension(tube_od.value),
                    "tube_length": parse_numeric_foot(tube_length.value),
                    "tube_material": tube_material.value,
                }
                if vessel:
                    index = self.temp_vessels.index(vessel)
                    self.temp_vessels[index] = new_vessel
                else:
                    self.temp_vessels.append(new_vessel)
                self.update_vessel_display()
                out.clear_output()
                if self.save_setup_button:
                    self.save_setup_button.layout.visibility = "visible"

            save_btn.on_click(save_vessel)
            display(
                widgets.VBox(
                    [
                        widgets.Label("Vessel Name:"),
                        vessel_name,
                        widgets.Label("Vessel Description:"),
                        vessel_desc,
                        widgets.Label("Pump Number:"),
                        pump_dropdown,
                        widgets.Label("ID of Tubing:"),
                        tube_id,
                        widgets.Label("OD of Tubing:"),
                        tube_od,
                        widgets.Label("Length of Tubing:"),
                        tube_length,
                        widgets.Label("Material of Tubing:"),
                        tube_material,
                        save_btn,
                    ]
                )
            )
        display(out)

    def update_vessel_display(self) -> None:
        children = []
        for vessel in self.temp_vessels:
            label = widgets.HTML(
                value=(
                    f"<div style='font-size: 14px; padding: 5px;'>"
                    f"{vessel['vessel_name']}: {vessel['vessel_desc']} "
                    f"(Pump {vessel['pump_number']}, {vessel['tube_material']})"
                    f"</div>"
                ),
                layout=widgets.Layout(width="60%"),
            )

            edit_btn = widgets.Button(
                description="Edit",
                button_style="info",
                style={"button_color": "#1E3A8A", "font_color": "black"},
                layout=widgets.Layout(width="80px"),
            )
            delete_btn = widgets.Button(
                description="Delete",
                button_style="danger",
                style={"button_color": "#D72638", "font_color": "black"},
                layout=widgets.Layout(width="80px"),
            )

            edit_btn.on_click(lambda b, v=vessel: self.vessel_window(b, vessel=v))
            delete_btn.on_click(lambda b, v=vessel: self.delete_vessel(v))

            vessel_entry = widgets.HBox(
                [label, edit_btn, delete_btn],
                layout=widgets.Layout(
                    margin="0 0 10px 0",
                    align_items="center",
                ),
            )
            children.append(vessel_entry)

        self.vessel_display.children = children

    def delete_vessel(self, vessel: Dict[str, Any]) -> None:
        if vessel in self.temp_vessels:
            self.temp_vessels.remove(vessel)
        self.update_vessel_display()

    def create_setup(self, b: widgets.Button) -> None:
        try:
            self._gather_inputs()
            missing = validate_required_fields_with_rmv(self.data)
            if missing:
                raise ValidationError(f"Missing fields: {missing}")
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
        self.data = {
            "apparatus_name": self.apparatus_name_widget.value,
            "reaction_mixture_vessel_name": self.product_vessel_name_widget.value,
            "reaction_mixture_vessel_desc": self.product_vessel_desc_widget.value,
            "vessels": self.temp_vessels[:],
        }
        if self.data["vessels"]:
            self.data["vessel1_name"] = self.data["vessels"][0]["vessel_name"]
            self.data["vessel1_desc"] = self.data["vessels"][0]["vessel_desc"]
            self.data["reaction_tube_id_raw"] = self.data["vessels"][0]["tube_id"]
            self.data["reaction_tube_od_raw"] = self.data["vessels"][0]["tube_od"]
            self.data["reaction_tube_material"] = self.data["vessels"][0][
                "tube_material"
            ]
            self.data["coil_a_raw"] = self.data["vessels"][0]["tube_length"]
            if len(self.data["vessels"]) > 1:
                self.data["vessel2_name"] = self.data["vessels"][1]["vessel_name"]
                self.data["vessel2_desc"] = self.data["vessels"][1]["vessel_desc"]
                self.data["coil_x_raw"] = self.data["vessels"][1]["tube_length"]
            else:
                self.data["vessel2_name"] = "Default Vessel2"
                self.data["vessel2_desc"] = "Default Vessel2"
                self.data["coil_x_raw"] = self.data["vessels"][0]["tube_length"]

    def _create_apparatus_config(self) -> Dict[str, Any]:
        return {
            "apparatus_name": self.data["apparatus_name"],
            "reaction_mixture_vessel": {
                "name": self.data["reaction_mixture_vessel_name"],
                "description": self.data["reaction_mixture_vessel_desc"],
            },
            "vessels": self.data["vessels"],
        }


class ApparatusCreator:
    def __init__(
        self, *pumps: HarvardSyringePump, data_file: Optional[str] = None
    ) -> None:
        self.pumps: List[HarvardSyringePump] = list(pumps)
        self.json_file: str = data_file if data_file else "apparatus_config.json"

    def create_apparatus(self) -> mw.Apparatus:
        import time
        from IPython import get_ipython
        import asyncio

        app = ComponentApp(self.pumps, self.json_file)
        app.create_widgets()
        while not app.setup_complete:
            time.sleep(0.1)
            if get_ipython():
                loop = asyncio.get_event_loop()
                loop.run_until_complete(get_ipython().kernel.do_one_iteration())
        with open(self.json_file, "r") as f:
            data = json.load(f)
        if "apparatus_config" not in data:
            raise ValueError("No apparatus configuration found")
        config = data["apparatus_config"]
        print(f"Using configuration: {config['apparatus_name']}")
        A = mw.Apparatus(config["apparatus_name"])
        reaction_mixture_vessel = mw.Vessel(
            config["reaction_mixture_vessel"]["description"],
            name=config["reaction_mixture_vessel"]["name"],
        )

        def make_tube(vessel_config: Dict[str, Any]) -> mw.Tube:
            return mw.Tube(
                length=vessel_config["tube_length"],
                ID=vessel_config["tube_id"],
                OD=vessel_config["tube_od"],
                material=vessel_config["tube_material"],
            )

        for vessel_config in config["vessels"]:
            tube = make_tube(vessel_config)
            pump_index = int(vessel_config["pump_number"])
            vessel = mw.Vessel(
                vessel_config["vessel_desc"], name=vessel_config["vessel_name"]
            )

            pump = self.pumps[pump_index]

            A.add(pump, vessel, tube)
            A.add(vessel, reaction_mixture_vessel, tube)

        return A


if __name__ == "__main__":
    from mechwolf.components.contrib.varian import VarianPump
    from mechwolf.components.contrib.freestep_pump import FreeStepPump

    pump_1 = HarvardSyringePump(
        syringe_volume="10 mL", syringe_diameter="14.567 mm", serial_port="COM1"
    )
    pump_2 = VarianPump(serial_port="COM2", max_rate="5 ml/min")
    pump_3 = FreeStepPump(serial_port="COM3")

    creator = ApparatusCreator(
        pump_1, pump_2, pump_3, data_file="apparatus_config.json"
    )
    creator.create_apparatus()
