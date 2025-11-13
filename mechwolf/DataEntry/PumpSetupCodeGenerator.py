import ipywidgets as widgets
from IPython.display import display, clear_output
from .SerialPortViewer import SerialPortViewer

class PumpCodeGenerator:
    """
    Interactive Jupyter notebook tool for configuring multiple pumps and 
    generating initialization code.
    """
    
    def __init__(self):
        # List to store configured pumps
        self.pumps = []
        
        # Initialize the serial port viewer
        self.serial_port_viewer = SerialPortViewer()
        
        # Create and display widgets
        self.create_widgets()
        self.display_ui()
        
    def create_widgets(self):
        """Create all the necessary widgets for the UI"""
        # Header
        self.header = widgets.HTML("<h1>MechWolf Pump Code Generator</h1>")
        
        # Pump type selection
        self.pump_type_dropdown = widgets.Dropdown(
            options=['HarvardSyringePump', 'FreeStepPump', 'VarianPump', 'ViciPump'],
            value='HarvardSyringePump',
            description='Pump Type:',
            layout=widgets.Layout(width='50%')
        )
        
        # Pump parameter widgets (we'll show/hide these based on selected pump type)
        # Common parameters
        self.serial_port_text = widgets.Text(
            value="COM1",
            description='Serial Port:',
            layout=widgets.Layout(width='50%')
        )
        
        # View serial ports button
        self.view_ports_button = widgets.Button(
            description='Show Available Serial Ports',
            button_style='info',
            icon='search',
            layout=widgets.Layout(width='auto')
        )
        
        # Serial ports output area
        self.serial_ports_output = widgets.Output(
            layout={'border': '1px solid #ddd', 'padding': '10px', 'margin': '10px 0', 'max_height': '150px', 'overflow': 'auto'}
        )
        
        # Harvard/FreeStep parameters
        self.syringe_volume_text = widgets.Text(
            value="3 mL",
            description='Syringe Volume:',
            layout=widgets.Layout(width='50%')
        )
        
        self.syringe_diameter_text = widgets.Text(
            value="10 mm",
            description='Syringe Diameter:',
            layout=widgets.Layout(width='50%')
        )
        
        # FreeStep specific parameters
        self.mcu_id_text = widgets.Text(
            value="",
            description='MCU ID:',
            layout=widgets.Layout(width='50%')
        )
        
        self.motor_id_text = widgets.Text(
            value="",
            description='Motor ID:',
            layout=widgets.Layout(width='50%')
        )
        
        # Varian parameters
        self.max_rate_text = widgets.Text(
            value="5 ml/min",
            description='Max Rate:',
            layout=widgets.Layout(width='50%')
        )
        
        self.unit_id_text = widgets.IntText(
            value=0,
            description='Unit ID:',
            layout=widgets.Layout(width='40%')
        )
        
        # Vici parameters
        self.volume_per_rev_text = widgets.Text(
            value="0.1 ml",
            description='Volume per Rev:',
            layout=widgets.Layout(width='50%')
        )
        
        # Add pump button
        self.add_pump_button = widgets.Button(
            description='Add Pump',
            button_style='success',
            icon='plus'
        )
        
        # Parameter box (will contain the right parameters based on pump type)
        self.param_box = widgets.VBox([])
        
        # Pump list area
        self.pump_list_output = widgets.Output(
            layout={'border': '1px solid #ddd', 'padding': '10px', 'margin': '10px 0', 'max_height': '200px', 'overflow': 'auto'}
        )
        
        # Code output area
        self.code_output = widgets.Output(
            layout={'border': '1px solid #ddd', 'padding': '10px', 'margin': '10px 0', 'max_height': '400px', 'overflow': 'auto'}
        )
        
        # Generate code button
        self.generate_code_button = widgets.Button(
            description='Generate Code',
            button_style='primary',
            icon='code'
        )
        
        # Clear all button
        self.clear_all_button = widgets.Button(
            description='Clear All',
            button_style='danger',
            icon='trash'
        )
        
        # Connect events
        self.pump_type_dropdown.observe(self.update_parameter_fields, names='value')
        self.add_pump_button.on_click(self.add_pump)
        self.generate_code_button.on_click(self.generate_code)
        self.clear_all_button.on_click(self.clear_all)
        self.view_ports_button.on_click(self.show_serial_ports)
        
        # Initialize parameter fields
        self.update_parameter_fields(None)
        
    def update_parameter_fields(self, change):
        """Update the parameter fields based on the selected pump type"""
        pump_type = self.pump_type_dropdown.value
        
        # Clear the parameter box
        fields = [
            widgets.HBox([self.serial_port_text, self.view_ports_button]),
            self.serial_ports_output
        ]
        
        if pump_type in ["HarvardSyringePump", "FreeStepPump"]:
            fields.extend([self.syringe_volume_text, self.syringe_diameter_text])
            
            if pump_type == "FreeStepPump":
                fields.extend([self.mcu_id_text, self.motor_id_text])
                
        elif pump_type == "VarianPump":
            fields.extend([self.max_rate_text, self.unit_id_text])
            
        elif pump_type == "ViciPump":
            fields.append(self.volume_per_rev_text)
        
        # Update the parameter box
        self.param_box.children = fields
    
    def show_serial_ports(self, _):
        """Display available serial ports"""
        with self.serial_ports_output:
            clear_output(wait=True)  # Use wait parameter for compatibility
            print("Scanning for available serial ports...")
            # Redirect stdout to capture the output from SerialPortViewer
            import io
            import sys
            
            # Redirect stdout to capture the output
            old_stdout = sys.stdout
            sys.stdout = mystdout = io.StringIO()
            
            # Run the serial port viewer
            self.serial_port_viewer.show_serial_ports()
            
            # Get the output and restore stdout
            ports_output = mystdout.getvalue()
            sys.stdout = old_stdout
            
            # Display the output
            if ports_output.strip():
                print(ports_output)
            else:
                print("No serial ports found.")
    
    def display_ui(self):
        """Display the user interface"""
        # Create a single container for all UI elements for better compatibility
        ui_container = widgets.VBox([
            self.header,
            # Pump configuration section
            widgets.VBox([
                widgets.HTML("<h3>Configure Pump</h3>"),
                self.pump_type_dropdown,
                self.param_box,
                self.add_pump_button
            ]),
            # Pump list section
            widgets.VBox([
                widgets.HTML("<h3>Configured Pumps</h3>"),
                self.pump_list_output
            ]),
            # Code generation section
            widgets.VBox([
                widgets.HTML("<h3>Generated Code</h3>"),
                widgets.HBox([self.generate_code_button, self.clear_all_button]),
                self.code_output
            ])
        ])
        
        display(ui_container)
    
    def add_pump(self, _):
        """Add a pump with the current configuration to the list"""
        pump_type = self.pump_type_dropdown.value
        serial_port = self.serial_port_text.value
        
        # Create a pump configuration dictionary based on the pump type
        pump_config = {
            "type": pump_type,
            "serial_port": serial_port
        }
        
        if pump_type in ["HarvardSyringePump", "FreeStepPump"]:
            pump_config["syringe_volume"] = self.syringe_volume_text.value
            pump_config["syringe_diameter"] = self.syringe_diameter_text.value
            
            if pump_type == "FreeStepPump":
                pump_config["mcu_id"] = self.mcu_id_text.value
                pump_config["motor_id"] = self.motor_id_text.value
        
        elif pump_type == "VarianPump":
            pump_config["max_rate"] = self.max_rate_text.value
            pump_config["unit_id"] = self.unit_id_text.value
        
        elif pump_type == "ViciPump":
            pump_config["volume_per_rev"] = self.volume_per_rev_text.value
        
        # Add the pump to the list
        self.pumps.append(pump_config)
        
        # Update the pump list display
        self.update_pump_list()
    
    def update_pump_list(self):
        """Update the pump list display"""
        with self.pump_list_output:
            clear_output(wait=True)  # Use wait parameter for compatibility
            
            if not self.pumps:
                print("No pumps configured yet. Add pumps using the form above.")
                return
            
            for i, pump in enumerate(self.pumps):
                print(f"Pump {i+1}: {pump['type']}")
                print(f"  Serial Port: {pump['serial_port']}")
                
                if pump['type'] in ["HarvardSyringePump", "FreeStepPump"]:
                    print(f"  Syringe Volume: {pump['syringe_volume']}")
                    print(f"  Syringe Diameter: {pump['syringe_diameter']}")
                    
                    if pump['type'] == "FreeStepPump":
                        print(f"  MCU ID: {pump['mcu_id']}")
                        print(f"  Motor ID: {pump['motor_id']}")
                
                elif pump['type'] == "VarianPump":
                    print(f"  Max Rate: {pump['max_rate']}")
                    print(f"  Unit ID: {pump['unit_id']}")
                
                elif pump['type'] == "ViciPump":
                    print(f"  Volume per Revolution: {pump['volume_per_rev']}")
                
                print()  # Empty line for spacing
                
                # Add a remove button for this pump
                remove_btn = widgets.Button(
                    description=f"Remove Pump {i+1}",
                    button_style='danger',
                    icon='trash',
                    layout=widgets.Layout(width='150px')
                )
                
                # Create a closure to capture the pump index
                def create_remove_handler(idx):
                    def handler(button):
                        self.remove_pump(idx)
                    return handler
                
                remove_btn.on_click(create_remove_handler(i))
                display(remove_btn)
                print()  # Empty line for spacing
    
    def remove_pump(self, index):
        """Remove a pump from the list by index"""
        if 0 <= index < len(self.pumps):
            del self.pumps[index]
            self.update_pump_list()
            
            # Also update the generated code
            self.generate_code(None)
    
    def generate_code(self, _):
        """Generate Python code for initializing the configured pumps"""
        with self.code_output:
            clear_output(wait=True)  # Use wait parameter for compatibility
            
            if not self.pumps:
                print("# No pumps configured yet. Add pumps using the form above.")
                return
            
            code = []
            
            # Add header and imports
            code.append("# Auto-generated pump initialization code")
            code.append("import mechwolf as mw")
            
            # Determine which imports we need
            pump_types = {pump["type"] for pump in self.pumps}
            
            for pump_type in sorted(pump_types):
                if pump_type == "HarvardSyringePump":
                    code.append("from mechwolf.components.contrib.harvardpump import HarvardSyringePump")
                elif pump_type == "FreeStepPump":
                    code.append("from mechwolf.components.contrib.freestep_pump import FreeStepPump")
                elif pump_type == "VarianPump":
                    code.append("from mechwolf.components.contrib.varian import VarianPump")
                elif pump_type == "ViciPump":
                    code.append("from mechwolf.components.contrib.vicipump import ViciPump")
            
            code.append("\n# Initialize pumps")
            
            # Generate initialization code for each pump
            for i, pump in enumerate(self.pumps):
                if pump["type"] == "HarvardSyringePump":
                    code.append(
                        f"pump_{i+1} = HarvardSyringePump(\"{pump['syringe_volume']}\", "
                        f"\"{pump['syringe_diameter']}\", "
                        f"serial_port=\"{pump['serial_port']}\")"
                    )
                elif pump["type"] == "FreeStepPump":
                    code.append(
                        f"pump_{i+1} = FreeStepPump(serial_port=\"{pump['serial_port']}\", "
                        f"mcu_id=\"{pump['mcu_id']}\", "
                        f"motor_id=\"{pump['motor_id']}\", "
                        f"syringe_volume=\"{pump['syringe_volume']}\", "
                        f"syringe_diameter=\"{pump['syringe_diameter']}\")"
                    )
                elif pump["type"] == "VarianPump":
                    code.append(
                        f"pump_{i+1} = VarianPump(\"{pump['serial_port']}\", "
                        f"\"{pump['max_rate']}\", "
                        f"unit_id={pump['unit_id']})"
                    )
                elif pump["type"] == "ViciPump":
                    code.append(
                        f"pump_{i+1} = ViciPump(\"{pump['serial_port']}\", "
                        f"\"{pump['volume_per_rev']}\")"
                    )
            
            # Add a list of all pumps
            pump_vars = [f"pump_{i+1}" for i in range(len(self.pumps))]
            if pump_vars:
                code.append("\n# Create a list of all pumps")
                code.append(f"pumps = [{', '.join(pump_vars)}]")
            
            # Print the generated code
            print("\n".join(code))
    
    def clear_all(self, _):
        """Clear all configured pumps"""
        self.pumps = []
        self.update_pump_list()
        
        with self.code_output:
            clear_output(wait=True)  # Use wait parameter for compatibility
            print("# All pumps cleared. Add new pumps using the form above.")

# Example usage
# from pump_setup_jupyter import PumpCodeGenerator
# generator = PumpCodeGenerator()
