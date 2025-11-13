# *************************************************************************
# FreeStep Controller Jupyter Calibration Tool
# Copyright(C) 4
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.If not, see < https://www.gnu.org/licenses/>.
# *************************************************************************

import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import time
import os
from mechwolf.components.contrib.freestep_3DSyringePump_controller import FreeStepController

class JupyterCalibrationTool:
    """Interactive Jupyter notebook tool for calibrating motors using FreeStep controller"""
    
    def __init__(self):
        self.controller = FreeStepController()
        
        # For storing selections
        self.selected_port = None
        self.selected_mcu = None
        self.selected_motor = None
        
        # For calibration trials
        self.first_trial = {"freq": None, "duration": None, "measurement": None, "ups": None}
        self.second_trial = {"freq": None, "duration": None, "measurement": None, "ups": None}
        
        # Initialize additional attributes
        self.step_pin = 0
        self.dir_pin = 0
        
        # Create widgets
        self.create_widgets()
        
        # Disable run buttons by default
        self.run_first_trial_button.disabled = True
        self.run_second_trial_button.disabled = True
        
        # Display main UI
        self.display_ui()
        
    def create_widgets(self):
        """Create all widgets for the UI"""
        # Status area
        self.status_output = widgets.Output(layout=widgets.Layout(width='100%', border='1px solid #ddd'))
        self.header = widgets.HTML("<h1>FreeStep Calibration Tool</h1>")
        
        # Storage information
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.storage_info = widgets.HTML(
            f"<div style='padding: 10px; background: #f8f8f8; border-left: 3px solid #2196F3;'>"
            f"<p><b>Data Storage:</b> Profiles are stored in JSON files in {base_dir}</p>"
            f"<p>• MCU profiles: MCUs.json</p>"
            f"<p>• Motor profiles: motors.json</p>"
            f"</div>"
        )
        
        # Port selection widgets
        self.port_dropdown = widgets.Dropdown(
            description='Port:',
            options=[],
            layout=widgets.Layout(width='50%')
        )
        self.refresh_ports_button = widgets.Button(
            description='Refresh Ports',
            button_style='info',
            icon='refresh'
        )
        self.connect_button = widgets.Button(
            description='Connect',
            button_style='success',
            icon='plug'
        )
        
        # Add disconnect button
        self.disconnect_button = widgets.Button(
            description='Disconnect Port',
            button_style='warning',
            icon='unlink',
            disabled=True  # Initially disabled since no port is connected
        )
        
        # MCU profile management widgets
        self.mcu_dropdown = widgets.Dropdown(
            description='MCU Profile:',
            options=[],
            layout=widgets.Layout(width='50%')
        )
        self.refresh_mcus_button = widgets.Button(
            description='Refresh MCUs',
            button_style='info',
            icon='refresh'
        )
        self.new_mcu_name = widgets.Text(
            description='New MCU Name:',
            value='New MCU',
            layout=widgets.Layout(width='40%')
        )
        self.add_mcu_button = widgets.Button(
            description='Add MCU Profile',
            button_style='success',
            icon='plus'
        )
        self.mcu_list_output = widgets.Output(
            layout={'border': '1px solid #ddd', 'padding': '10px', 'margin': '10px 0'}
        )
        
        # Motor profile management widgets
        self.motor_dropdown = widgets.Dropdown(
            description='Motor Profile:',
            options=[],
            layout=widgets.Layout(width='50%')
        )
        self.refresh_motors_button = widgets.Button(
            description='Refresh Motors',
            button_style='info',
            icon='refresh'
        )
        self.new_motor_name = widgets.Text(
            description='New Motor Name:',
            value='New Motor',
            layout=widgets.Layout(width='60%')
        )
        self.add_motor_button = widgets.Button(
            description='Add Motor Profile',
            button_style='success',
            icon='plus'
        )
        self.motor_list_output = widgets.Output(
            layout={'border': '1px solid #ddd', 'padding': '10px', 'margin': '10px 0'}
        )
        
        # Calibration selection widgets - simplify to just motor selection
        self.calibration_motor_dropdown = widgets.Dropdown(
            description='Motor Profile:',
            options=[],
            layout=widgets.Layout(width='50%')
        )
        
        self.calibration_mcu_info = widgets.HTML(
            value="<p>No motor selected</p>",
            layout=widgets.Layout(width='100%')
        )
        
        # Pin configuration widgets
        self.step_pin_input = widgets.IntText(
            description='Step Pin:',
            value=0,
            layout=widgets.Layout(width='40%')
        )
        self.dir_pin_input = widgets.IntText(
            description='Dir Pin:',
            value=0,
            layout=widgets.Layout(width='40%')
        )
        self.configure_pins_button = widgets.Button(
            description='Configure Pins',
            button_style='primary',
            icon='wrench'
        )
        
        # Calibration trial widgets - First trial
        self.first_trial_freq_input = widgets.FloatText(
            description='Frequency (Hz):',
            value=100.0,
            layout=widgets.Layout(width='40%')
        )
        self.first_trial_duration_input = widgets.FloatText(
            description='Duration (s):',
            value=10.0,
            layout=widgets.Layout(width='40%')
        )
        self.first_trial_measurement_input = widgets.FloatText(
            description='Volume (mL):',
            value=0.0,
            layout=widgets.Layout(width='40%')
        )
        self.run_first_trial_button = widgets.Button(
            description='Run First Trial',
            button_style='warning',
            icon='play'
        )
        
        # Calibration trial widgets - Second trial
        self.second_trial_freq_input = widgets.FloatText(
            description='Frequency (Hz):',
            value=500.0,
            layout=widgets.Layout(width='40%')
        )
        self.second_trial_duration_input = widgets.FloatText(
            description='Duration (s):',
            value=10.0,
            layout=widgets.Layout(width='40%')
        )
        self.second_trial_measurement_input = widgets.FloatText(
            description='Volume (mL):',
            value=0.0,
            layout=widgets.Layout(width='40%')
        )
        self.run_second_trial_button = widgets.Button(
            description='Run Second Trial',
            button_style='warning',
            icon='play'
        )
        
        # Calculate calibration button
        self.calculate_button = widgets.Button(
            description='Calculate Calibration',
            button_style='success',
            icon='calculator'
        )
        
        # Calibration results display
        self.calibration_results = widgets.Output(
            layout={'border': '1px solid #ddd', 'padding': '10px'}
        )
        
        # Testing widgets
        self.test_mcu_dropdown = widgets.Dropdown(
            description='MCU Profile:',
            options=[],
            layout=widgets.Layout(width='50%')
        )
        self.test_motor_dropdown = widgets.Dropdown(
            description='Motor Profile:',
            options=[],
            layout=widgets.Layout(width='50%')
        )
        self.test_ups_input = widgets.FloatText(
            description='Flow Rate (mL/min):',
            value=1.0,
            layout=widgets.Layout(width='40%')
        )
        self.test_direction = widgets.RadioButtons(
            options=['forward', 'backward'],
            description='Direction:',
            value='forward'
        )
        self.test_duration_input = widgets.FloatText(
            description='Duration (s):',
            value=5.0,
            layout=widgets.Layout(width='40%')
        )
        
        # Add syringe diameter override for testing
        self.test_syringe_diameter = widgets.FloatText(
            description='Custom Inner Diameter (mm):',
            value=0.0,
            min=0.0,
            step=0.1,
            layout=widgets.Layout(width='50%'),
            placeholder='Leave 0 to use calibrated diameter'
        )
        self.test_use_calibrated_checkbox = widgets.Checkbox(
            value=True,
            description='Use calibrated syringe data',
            layout=widgets.Layout(width='60%')
        )
        
        self.run_test_button = widgets.Button(
            description='Run Test',
            button_style='primary',
            icon='play'
        )
        self.stop_test_button = widgets.Button(
            description='Stop Motor',
            button_style='danger',
            icon='stop'
        )
        
        # MCU profile editing widgets
        self.edit_mcu_name = widgets.Text(
            description='Edit Name:',
            layout=widgets.Layout(width='40%'),
            disabled=True
        )
        self.save_mcu_button = widgets.Button(
            description='Save Changes',
            button_style='success',
            icon='save',
            disabled=True
        )
        self.delete_mcu_button = widgets.Button(
            description='Delete MCU',
            button_style='danger',
            icon='trash',
            disabled=True
        )
        self.current_mcu_id = None
        
        # Motor profile editing widgets - Move these here, before their references
        self.edit_motor_name = widgets.Text(
            description='Edit Name:',
            layout=widgets.Layout(width='60%'),
            disabled=True
        )
        
        # Add MCU association dropdown for editing
        self.edit_motor_mcu_dropdown = widgets.Dropdown(
            description='Associated MCU:',
            options=[],
            layout=widgets.Layout(width='50%'),
            disabled=True
        )
        
        self.edit_motor_step_pin = widgets.IntText(
            description='Step Pin:',
            value=0,
            layout=widgets.Layout(width='40%'),
            disabled=True
        )
        
        self.edit_motor_dir_pin = widgets.IntText(
            description='Dir Pin:',
            value=0,
            layout=widgets.Layout(width='40%'),
            disabled=True
        )
        
        self.update_pins_button = widgets.Button(
            description='Update Pins',
            button_style='primary',
            icon='wrench',
            disabled=True
        )
        
        # Create save and delete buttons for motors 
        self.save_motor_button = widgets.Button(
            description='Save Changes',
            button_style='success',
            icon='save',
            disabled=True
        )
        
        self.delete_motor_button = widgets.Button(
            description='Delete Motor',
            button_style='danger',
            icon='trash',
            disabled=True
        )
        
        self.current_motor_id = None
        
        # Motor creation/editing widgets
        self.new_motor_step_pin = widgets.IntText(
            description='Step Pin:',
            value=0,
            layout=widgets.Layout(width='40%')
        )
        self.new_motor_dir_pin = widgets.IntText(
            description='Dir Pin:',
            value=0,
            layout=widgets.Layout(width='40%')
        )
        
        # Add motor-MCU association widgets
        self.associate_title = widgets.HTML("<h3>Associate Motor with MCU</h3>")
        self.associate_motor_dropdown = widgets.Dropdown(
            description='Motor:',
            options=[],
            layout=widgets.Layout(width='50%')
        )
        self.associate_mcu_dropdown = widgets.Dropdown(
            description='MCU:',
            options=[],
            layout=widgets.Layout(width='50%')
        )
        self.associate_step_pin = widgets.IntText(
            description='Step Pin:',
            value=0,
            layout=widgets.Layout(width='40%')
        )
        self.associate_dir_pin = widgets.IntText(
            description='Dir Pin:',
            value=0,
            layout=widgets.Layout(width='40%')
        )
        self.associate_button = widgets.Button(
            description='Associate Motor with MCU',
            button_style='primary',
            icon='link'
        )
        
        # Syringe information widgets for calibration
        self.syringe_info_header = widgets.HTML("<h3>Syringe Information</h3>")
        self.syringe_brand_input = widgets.Text(
            description='Brand/Manufacturer:',
            value='',
            placeholder='e.g., BD, Hamilton',
            layout=widgets.Layout(width='60%')
        )
        self.syringe_model_input = widgets.Text(
            description='Model/Type:',
            value='',
            placeholder='e.g., Plastic, Glass, Model #',
            layout=widgets.Layout(width='60%')
        )
        self.syringe_volume_input = widgets.FloatText(
            description='Volume (mL):',
            value=10.0,
            min=0.001,
            layout=widgets.Layout(width='40%')
        )
        self.syringe_diameter_input = widgets.FloatText(
            description='Inner Diameter (mm):',  # Changed to Inner Diameter
            value=15.0,
            min=0.1,
            layout=widgets.Layout(width='40%')
        )
        
        # Tab layout
        self.tabs = widgets.Tab()
        
        # Add calibration details output area for the testing tab with increased height
        self.test_calibration_details = widgets.Output(
            layout=widgets.Layout(
                border='1px solid #ddd',
                padding='10px',
                width='100%',
                height='300px',  # Increased height to show more information
                overflow='auto'
            )
        )
        
        # Add button event handlers - Move all these after all widgets are created
        self.refresh_ports_button.on_click(self.refresh_ports)
        self.connect_button.on_click(self.connect_port)
        self.disconnect_button.on_click(self.disconnect_port)  # Add handler for disconnect button
        self.refresh_mcus_button.on_click(self.refresh_mcus)
        self.add_mcu_button.on_click(self.add_mcu)
        self.refresh_motors_button.on_click(self.refresh_motors)
        self.add_motor_button.on_click(self.add_motor)
        self.configure_pins_button.on_click(self.configure_pins)
        self.run_first_trial_button.on_click(self.run_first_trial)
        self.run_second_trial_button.on_click(self.run_second_trial)
        self.calculate_button.on_click(self.calculate_calibration)
        self.run_test_button.on_click(self.run_test)
        self.stop_test_button.on_click(self.stop_motor)
        self.associate_button.on_click(self.associate_motor_with_mcu)
        self.update_pins_button.on_click(self.update_motor_pins)
        
        # MCU and motor editing event handlers
        self.calibration_motor_dropdown.observe(self.calibration_motor_changed, names='value')
        self.test_mcu_dropdown.observe(self.update_test_selections, names='value')
        self.test_motor_dropdown.observe(self.test_motor_dropdown_changed, names='value')
        self.test_ups_input.observe(self.update_flow_rate, names='value')
        self.test_syringe_diameter.observe(self.update_custom_diameter, names='value')
        self.save_mcu_button.on_click(self.save_mcu_changes)
        self.delete_mcu_button.on_click(self.delete_mcu)
        self.save_motor_button.on_click(self.save_motor_changes)
        self.delete_motor_button.on_click(self.delete_motor)
        
        # Add event handler for the checkbox
        self.test_use_calibrated_checkbox.observe(self.toggle_diameter_field, names='value')
        
        # Initial data load
        self.refresh_ports()
        self.refresh_mcus()
        self.refresh_motors()
        self.display_mcu_list()
        self.display_motor_list()
        self.update_association_dropdowns()
    
    def display_ui(self):
        """Display the main UI with tabs"""
        # Import visualization module here to prevent circular imports
        from mechwolf.components.contrib.calibration_visualizations import CalibrationVisualizer
        
        # Create the visualizer instance
        self.visualizer = CalibrationVisualizer(self.controller)
        
        # Create the overview tab first
        overview_tab = self.visualizer.create_overview_tab()
        
        # Connection tab (shared across all functions)
        connection_tab = widgets.VBox([
            self.storage_info,
            widgets.HTML("<h3>Serial Port Connection</h3>"),
            widgets.HBox([self.port_dropdown, self.refresh_ports_button, self.connect_button, self.disconnect_button])
        ])
        
        # MCU Profiles tab
        mcu_profiles_tab = widgets.VBox([
            widgets.HTML("<h3>Create/Manage MCU Profiles</h3>"),
            widgets.HBox([self.new_mcu_name, self.add_mcu_button, self.refresh_mcus_button]),
            widgets.HTML("<h3>Edit Selected MCU</h3>"),
            widgets.HBox([self.edit_mcu_name, self.save_mcu_button, self.delete_mcu_button]),
            widgets.HTML("<h3>Available MCU Profiles</h3>"),
            self.mcu_list_output
        ])
        
        # Motor Profiles tab - reorganized for simpler flow
        motor_profiles_tab = widgets.VBox([
            widgets.HTML("<h3>Create New Motor Profile</h3>"),
            widgets.HBox([self.new_motor_name, self.add_motor_button]),
            widgets.HBox([self.refresh_motors_button]),
            
            # Edit section moved up before association
            widgets.HTML("<h3>Edit Motor & MCU Association</h3>"),
            widgets.HTML("<p>Edit motor name and update associated MCU pins</p>"),
            widgets.HBox([self.edit_motor_name]),
            widgets.HBox([self.edit_motor_mcu_dropdown]),
            widgets.HBox([self.edit_motor_step_pin, self.edit_motor_dir_pin]),
            widgets.HBox([self.update_pins_button, self.save_motor_button, self.delete_motor_button]),
            
            # Association section for new associations
            self.associate_title,
            widgets.HTML("<p>Associate a motor with a new MCU and set its pins</p>"),
            widgets.HBox([self.associate_motor_dropdown, self.associate_mcu_dropdown]),
            widgets.HBox([self.associate_step_pin, self.associate_dir_pin]),
            self.associate_button,
            
            widgets.HTML("<h3>Available Motor Profiles</h3>"),
            self.motor_list_output
        ])
        
        # Calibration tab - modified to include syringe information
        calibration_tab = widgets.VBox([
            widgets.HTML("<h3>Select Motor for Calibration</h3>"),
            self.calibration_motor_dropdown,
            self.calibration_mcu_info,
            
            # Syringe information section
            self.syringe_info_header,
            widgets.HTML("<p>Please provide information about the syringe used for calibration:</p>"),
            self.syringe_brand_input,
            self.syringe_model_input,
            widgets.HBox([self.syringe_volume_input, self.syringe_diameter_input]),
            
            widgets.HTML("<h3>First Calibration Trial</h3>"),
            widgets.HBox([self.first_trial_freq_input, self.first_trial_duration_input]),
            self.first_trial_measurement_input,
            self.run_first_trial_button,
            widgets.HTML("<h3>Second Calibration Trial</h3>"),
            widgets.HBox([self.second_trial_freq_input, self.second_trial_duration_input]),
            self.second_trial_measurement_input,
            self.run_second_trial_button,
            widgets.HTML("<h3>Calibration Results</h3>"),
            self.calculate_button,
            self.calibration_results
        ])
        
        # Testing tab with side-by-side layout for parameters and calibration details
        testing_tab = widgets.VBox([
            widgets.HTML("<h3>Select Profiles for Testing</h3>"),
            widgets.HBox([self.test_mcu_dropdown, self.test_motor_dropdown]),
            
            # Place Test Parameters header above the HBox layout that contains
            # both the parameters and calibration details
            widgets.HTML("<h3>Test Parameters</h3>"),
            
            # Main HBox for side-by-side layout
            widgets.HBox([
                # Left side - all the input controls (40% width)
                widgets.VBox([
                    self.test_ups_input,
                    widgets.HTML("<h4>Syringe Options</h4>"),
                    self.test_use_calibrated_checkbox,
                    self.test_syringe_diameter,
                    widgets.HTML("<h4>Run Parameters</h4>"),
                    self.test_direction,
                    self.test_duration_input,
                    widgets.HBox([self.run_test_button, self.stop_test_button])
                ], layout=widgets.Layout(width='40%')),
                
                # Right side - calibration details (60% width)
                widgets.VBox([
                    widgets.HTML("<h4>Calibration Details</h4>"),
                    self.test_calibration_details
                ], layout=widgets.Layout(width='60%'))
            ])
        ])
        
        # Add the visualization tab using the visualizer layout
        visualization_tab = self.visualizer.create_tab_layout()
        
        # Set up the tabs including the new overview tab at the beginning
        self.tabs.children = [overview_tab, connection_tab, mcu_profiles_tab, motor_profiles_tab, calibration_tab, testing_tab, visualization_tab]
        self.tabs.set_title(0, 'Overview')
        self.tabs.set_title(1, 'Connection')
        self.tabs.set_title(2, 'MCU Profiles')
        self.tabs.set_title(3, 'Motor Profiles')
        self.tabs.set_title(4, 'Calibration')
        self.tabs.set_title(5, 'Testing')
        self.tabs.set_title(6, 'Visualization')
        
        # Display everything
        display(self.header)
        display(self.status_output)
        display(self.tabs)
    
    def log(self, message, clear=False):
        """Log a message to the status output"""
        with self.status_output:
            if clear:
                clear_output()
            print(message)
    
    def refresh_ports(self, _=None):
        """Refresh the available ports"""
        self.log("Refreshing available ports...", clear=True)
        ports = self.controller.list_ports()
        
        # Update the dropdown
        self.port_dropdown.options = [('Select Port', None)] + [(p['path'], p['path']) for p in ports]
        self.port_dropdown.value = None
        
        # Disable disconnect button when refreshing ports
        self.disconnect_button.disabled = True
        self.selected_port = None
        
        self.log(f"Found {len(ports)} ports")
    
    def refresh_mcus(self, _=None):
        """Refresh the available MCU profiles"""
        self.log("Loading MCU profiles...", clear=True)
        mcus = self.controller.get_mcus()
        
        # Update MCU dropdowns
        options = [('Select MCU', None)] + [(mcu['name'], mcu) for mcu in mcus]
        self.mcu_dropdown.options = options
        self.test_mcu_dropdown.options = options
        self.associate_mcu_dropdown.options = options  # Update association dropdown
        
        # Clear selections
        self.mcu_dropdown.value = None
        self.test_mcu_dropdown.value = None
        self.associate_mcu_dropdown.value = None  # Reset association selection
        
        # Update the MCU list display
        self.display_mcu_list()
        
        self.log(f"Loaded {len(mcus)} MCU profiles")
    
    def refresh_motors(self, _=None):
        """Refresh the available motor profiles"""
        self.log("Loading motor profiles...", clear=True)
        motors = self.controller.get_motors()
        
        # Update all motor dropdowns
        options = [('Select Motor', None)] + [(motor['name'], motor) for motor in motors]
        self.motor_dropdown.options = options
        self.calibration_motor_dropdown.options = options
        self.associate_motor_dropdown.options = options  # Update association dropdown
        
        # Reset selections
        self.motor_dropdown.value = None
        self.calibration_motor_dropdown.value = None
        self.associate_motor_dropdown.value = None  # Reset association selection
        
        # Update the motor list display
        self.display_motor_list()
        
        self.log(f"Loaded {len(motors)} motor profiles")
    
    def add_mcu(self, _=None):
        """Add a new MCU profile"""
        name = self.new_mcu_name.value.strip()
        if not name:
            self.log("Please enter a valid name for the new MCU profile", clear=True)
            return
        
        self.log(f"Adding new MCU profile '{name}'...", clear=True)
        unique_id = self.controller.add_mcu(name)
        
        if unique_id:
            self.log(f"Added MCU profile '{name}' with ID {unique_id}")
            self.refresh_mcus()  # Refresh the dropdown
            self.new_mcu_name.value = "New MCU"  # Reset the input field
        else:
            self.log("Failed to add MCU profile")
    
    def add_motor(self, _=None):
        """Add a new motor profile with just a name"""
        name = self.new_motor_name.value.strip()
        
        if not name:
            self.log("Please enter a valid name for the new motor profile", clear=True)
            return
        
        self.log(f"Adding new motor profile '{name}'...", clear=True)
        unique_id = self.controller.add_motor(name)
        
        if unique_id:
            self.log(f"Added motor profile '{name}' with ID {unique_id}")
            self.log("To use this motor, please associate it with an MCU using the section below.")
            
            self.refresh_motors()  # Refresh the dropdown
            
            # Reset the input fields
            self.new_motor_name.value = "New Motor"
        else:
            self.log("Failed to add motor profile")
    
    def connect_port(self, _):
        """Connect to the selected port"""
        if not self.port_dropdown.value:
            self.log("Please select a port first", clear=True)
            return
        
        port = self.port_dropdown.value
        self.log(f"Connecting to {port}...", clear=True)
        
        # First disconnect any existing connections to ensure clean state
        if self.selected_port:
            self.controller.disconnect_port(self.selected_port)
            self.selected_port = None
        
        if self.controller.connect_port(port):
            self.selected_port = port
            self.log(f"Connected to {port} successfully")
            # Enable disconnect button after successful connection
            self.disconnect_button.disabled = False
        else:
            self.log(f"Failed to connect to {port}")
    
    def disconnect_port(self, _):
        """Disconnect from the currently connected port"""
        if not self.selected_port:
            self.log("No port is currently connected", clear=True)
            return
        
        port = self.selected_port
        self.log(f"Disconnecting from {port}...", clear=True)
        
        # Try to stop any motors first to avoid leaving them running
        if self.selected_mcu and self.selected_motor:
            try:
                self.controller.stop_command(self.selected_port, self.selected_mcu, self.selected_motor)
                time.sleep(0.5)  # Give time for stop command to process
            except Exception as e:
                self.log(f"Warning: Failed to stop motors: {str(e)}")
        
        # Now disconnect from the port
        if self.controller.disconnect_port(self.selected_port):
            self.log(f"Disconnected from {port} successfully")
            self.selected_port = None
            # Disable disconnect button after disconnection
            self.disconnect_button.disabled = True
            
            # Also disable run buttons since no port is connected
            self.run_first_trial_button.disabled = True
            self.run_second_trial_button.disabled = True
        else:
            self.log(f"Failed to disconnect from {port}")
    
    def run_calibration_trial(self, trial_name):
        """Run a calibration trial"""
        # Get the selected motor
        selected_motor = self.selected_motor
        
        if not self.selected_port:
            self.log("Please connect to a port first", clear=True)
            return
            
        if not self.selected_mcu:
            self.log("No MCU available for this motor. Configure the motor in an MCU first.", clear=True)
            return
            
        if not selected_motor:
            self.log("Please select a motor profile first", clear=True)
            return
        
        # Get trial parameters based on which trial we're running
        if trial_name == "First":
            freq = self.first_trial_freq_input.value
            duration = self.first_trial_duration_input.value
        else:
            freq = self.second_trial_freq_input.value
            duration = self.second_trial_duration_input.value
        
        # Ensure step and dir pins are integers
        step_pin = int(self.step_pin)
        dir_pin = int(self.dir_pin)
        
        # Use the direct send_formatted_command method that formats JSON correctly for Arduino
        self.log(f"Running {trial_name} trial at {freq} Hz for {duration} seconds...", clear=True)
        
        # First stop any running motor to clear buffer and ensure clean state
        self.controller.stop_command(self.selected_port, self.selected_mcu, self.selected_motor)
        time.sleep(0.5)  # Give time for stop command to process
        
        # Create a command directly compatible with the Arduino's parser
        success = self.controller.serial_manager.send_formatted_command(
            self.selected_port,  # Port name 
            "timed",             # Command type
            step_pin,            # Step pin
            dir_pin,             # Direction pin
            freq,                # Frequency in Hz
            duration,            # Duration value
            "s",                 # Time unit (seconds)
            "forward"            # Direction
        )
        
        if not success:
            self.log("Failed to send command to the device. Check connections.", clear=True)
            return
        
        self.log(f"Sent command to {self.selected_port}: timed run at {freq}Hz for {duration}s", clear=False)
            
        # Start a countdown timer
        for remaining in range(int(duration), 0, -1):
            self.log(f"Running... {remaining}s remaining", clear=True)
            time.sleep(1)
        
        # Stop the pump after the trial to ensure it's not left running
        self.controller.stop_command(self.selected_port, self.selected_mcu, self.selected_motor)
        time.sleep(0.5)  # Give time for stop command to process
            
        self.log(f"{trial_name} trial complete. Please enter the measured volume.", clear=True)

    def display_mcu_list(self):
        """Display the list of MCU profiles in the MCU tab"""
        with self.mcu_list_output:
            clear_output()
            mcus = self.controller.get_mcus()
            if not mcus:
                print("No MCU profiles found.")
                return
            
            # Create a simple interactive list
            for i, mcu in enumerate(mcus):
                mcu_id = mcu.get('uniqueID')
                
                # Print profile info with an edit button
                print(f"{i+1}. {mcu.get('name')} (ID: {mcu_id})")
                
                # Create and display an edit button for this MCU
                edit_btn = widgets.Button(
                    description="Edit",
                    button_style='info',
                    layout=widgets.Layout(width='80px')
                )
                
                # Create a closure to capture the mcu_id
                def create_mcu_handler(mcu_id):
                    def handler(button):
                        self.edit_mcu(mcu_id)
                    return handler
                    
                # Add click handler with the captured ID
                edit_btn.on_click(create_mcu_handler(mcu_id))
                
                display(edit_btn)
                
                if 'motors' in mcu and mcu['motors']:
                    print("   Configured motors:")
                    for motor in mcu['motors']:
                        print(f"   - {motor.get('name')} (Step: {motor.get('step')}, Dir: {motor.get('dir')})")
                else:
                    print("   No motors configured")
                print("")

    def display_motor_list(self):
        """Display the list of motor profiles in the Motor tab"""
        with self.motor_list_output:
            clear_output()
            motors = self.controller.get_motors()
            if not motors:
                print("No motor profiles found.")
                return
            
            # Create a simple interactive list
            for i, motor in enumerate(motors):
                motor_id = motor.get('uniqueID')
                calibrated = "Yes" if motor.get("calibrated") else "No"
                
                # Print profile info
                print(f"{i+1}. {motor.get('name')} (ID: {motor_id})")
                
                # Create and display an edit button for this motor
                edit_btn = widgets.Button(
                    description="Edit",
                    button_style='info',
                    layout=widgets.Layout(width='80px')
                )
                
                # Create a closure to capture the motor_id
                def create_motor_handler(motor_id):
                    def handler(button):
                        self.edit_motor(motor_id)
                    return handler
                    
                # Add click handler with the captured ID
                edit_btn.on_click(create_motor_handler(motor_id))
                
                display(edit_btn)
                
                print(f"   Calibrated: {calibrated}")
                
                # Display syringe info if available
                if "syringeInfo" in motor:
                    si = motor["syringeInfo"]
                    if "innerDiameterMM" in si:  # Use the new key if available
                        diameter_key = "innerDiameterMM"
                        diameter_label = "inner dia"
                    else:  # For backwards compatibility with old saved profiles
                        diameter_key = "diameterMM"
                        diameter_label = "dia"
                    print(f"   Syringe: {si.get('brand')} {si.get('model')}, {si.get('volumeML')}mL, {si.get(diameter_key)}mm {diameter_label}")
                    print(f"   Calibration Date: {si.get('calibrationDate', 'Unknown')}")
                
                # Find if this motor has pins configured in any MCU
                mcus = self.controller.get_mcus()
                for mcu in mcus:
                    for mcu_motor in mcu.get('motors', []):
                        if mcu_motor.get('uniqueID') == motor_id:
                            print(f"   Used in MCU '{mcu.get('name')}' with Step: {mcu_motor.get('step')}, Dir: {mcu_motor.get('dir')}")
                
                if calibrated == "Yes":
                    min_ups = motor.get("minUPS")
                    max_ups = motor.get("maxUPS")
                    print(f"   Flow Rate Range: {min_ups:.6f} to {max_ups:.2f} mL/min")
                print("")
    
    def edit_mcu(self, mcu_id):
        """Enable editing for the selected MCU"""
        mcus = self.controller.get_mcus()
        mcu = next((m for m in mcus if m.get('uniqueID') == mcu_id), None)
        
        if mcu:
            self.current_mcu_id = mcu_id
            self.edit_mcu_name.value = mcu.get('name', '')
            self.edit_mcu_name.disabled = False
            self.save_mcu_button.disabled = False
            self.delete_mcu_button.disabled = False
            self.log(f"Editing MCU: {mcu.get('name')}", clear=True)
    
    def save_mcu_changes(self, _):
        """Save changes to the edited MCU"""
        if not self.current_mcu_id:
            return
        
        mcus = self.controller.get_mcus()
        mcu = next((m for m in mcus if m.get('uniqueID') == self.current_mcu_id), None)
        
        if mcu:
            mcu['name'] = self.edit_mcu_name.value.strip()
            self.controller.profile_manager.save_mcus(mcus)
            self.refresh_mcus()
            self.log(f"Saved changes to MCU: {mcu['name']}", clear=True)
            
            # Reset the edit fields
            self.current_mcu_id = None
            self.edit_mcu_name.value = ''
            self.edit_mcu_name.disabled = True
            self.save_mcu_button.disabled = True
            self.delete_mcu_button.disabled = True
    
    def delete_mcu(self, _):
        """Delete the selected MCU"""
        if not self.current_mcu_id:
            return
        
        mcus = self.controller.get_mcus()
        mcu = next((m for m in mcus if m.get('uniqueID') == self.current_mcu_id), None)
        
        if mcu:
            mcu_name = mcu.get('name')
            mcus = [m for m in mcus if m.get('uniqueID') != self.current_mcu_id]
            self.controller.profile_manager.save_mcus(mcus)
            self.log(f"Deleted MCU: {mcu_name}", clear=True)
            self.refresh_mcus()
            
            # Reset the edit fields
            self.current_mcu_id = None
            self.edit_mcu_name.value = ''
            self.edit_mcu_name.disabled = True
            self.save_mcu_button.disabled = True
            self.delete_mcu_button.disabled = True
    
    def edit_motor(self, motor_id):
        """Enable editing for the selected motor with MCU associations"""
        motors = self.controller.get_motors()
        motor = next((m for m in motors if m.get('uniqueID') == motor_id), None)
        
        if motor:
            self.current_motor_id = motor_id
            self.edit_motor_name.value = motor.get('name', '')
            
            # Enable the editing widgets
            self.edit_motor_name.disabled = False
            self.save_motor_button.disabled = False
            self.delete_motor_button.disabled = False
            
            # Find MCU associations for this motor
            mcus = self.controller.get_mcus()
            associated_mcus = []
            
            for mcu in mcus:
                for mcu_motor in mcu.get('motors', []):
                    if mcu_motor.get('uniqueID') == motor_id:
                        associated_mcus.append((mcu['name'], mcu))
            
            # Update the MCU dropdown with associated MCUs
            if associated_mcus:
                self.edit_motor_mcu_dropdown.options = [('Select MCU', None)] + associated_mcus
                self.edit_motor_mcu_dropdown.disabled = False
                self.edit_motor_mcu_dropdown.observe(self.motor_mcu_association_changed, names='value')
            else:
                self.edit_motor_mcu_dropdown.options = [('No MCU Associations', None)]
                self.edit_motor_mcu_dropdown.disabled = True
                self.edit_motor_step_pin.disabled = True
                self.edit_motor_dir_pin.disabled = True
                self.update_pins_button.disabled = True
            
            self.log(f"Editing motor: {motor.get('name')}", clear=True)
            
            # Display syringe info if available
            if "syringeInfo" in motor:
                si = motor["syringeInfo"]
                self.log(f"Calibrated with {si.get('brand')} {si.get('model')} syringe ({si.get('volumeML')}mL, {si.get('diameterMM')}mm dia)")
                
            if not associated_mcus:
                self.log("This motor is not associated with any MCU. Use the Associate Motor with MCU section below.")
    
    def motor_mcu_association_changed(self, change):
        """Handle selection change in the MCU association dropdown"""
        selected_mcu = change.new
        
        if not selected_mcu or not self.current_motor_id:
            self.edit_motor_step_pin.disabled = True
            self.edit_motor_dir_pin.disabled = True
            self.update_pins_button.disabled = True
            return
        
        # Find the motor in the selected MCU
        for motor in selected_mcu.get('motors', []):
            if motor.get('uniqueID') == self.current_motor_id:
                # Found the motor in this MCU, fill in the current pin values
                self.edit_motor_step_pin.value = motor.get('step', 0)
                self.edit_motor_dir_pin.value = motor.get('dir', 0)
                self.edit_motor_step_pin.disabled = False
                self.edit_motor_dir_pin.disabled = False
                self.update_pins_button.disabled = False
                break
    
    def update_motor_pins(self, _):
        """Update pin assignments for a motor in the selected MCU"""
        if not self.current_motor_id:
            return
            
        selected_mcu = self.edit_motor_mcu_dropdown.value
        if not selected_mcu:
            self.log("Please select an MCU", clear=True)
            return
        
        step_pin = self.edit_motor_step_pin.value
        dir_pin = self.edit_motor_dir_pin.value
        
        # Find the motor in the MCU
        motor_updated = False
        for motor in selected_mcu.get('motors', []):
            if motor.get('uniqueID') == self.current_motor_id:
                motor['step'] = step_pin
                motor['dir'] = dir_pin
                motor_updated = True
                break
        
        if motor_updated:
            # Save the updated MCU profile
            self.controller.profile_manager.update_mcu(selected_mcu)
            self.log(f"Updated pin assignments in MCU '{selected_mcu.get('name')}': step={step_pin}, dir={dir_pin}")
            
            # Refresh displays
            self.display_mcu_list()
            self.display_motor_list()
        else:
            self.log("Error: Motor not found in selected MCU", clear=True)
    
    def save_motor_changes(self, _):
        """Save changes to the edited motor name"""
        if not self.current_motor_id:
            return
        
        motors = self.controller.get_motors()
        motor = next((m for m in motors if m.get('uniqueID') == self.current_motor_id), None)
        
        if motor:
            new_name = self.edit_motor_name.value.strip()
            if not new_name:
                self.log("Please enter a valid name", clear=True)
                return
                
            motor['name'] = new_name
            self.controller.profile_manager.save_motors(motors)
            
            # Update name in all MCUs where this motor is used
            mcus = self.controller.get_mcus()
            for mcu in mcus:
                for mcu_motor in mcu.get('motors', []):
                    if mcu_motor.get('uniqueID') == self.current_motor_id:
                        mcu_motor['name'] = new_name  # Update name to match
                        self.controller.profile_manager.update_mcu(mcu)
                    
            self.log(f"Saved changes to motor name: {motor['name']}", clear=True)
            self.refresh_mcus()
            self.refresh_motors()
            
            # Reset the edit fields
            self.current_motor_id = None
            self.edit_motor_name.value = ''
            self.edit_motor_name.disabled = True
            self.save_motor_button.disabled = True
            self.delete_motor_button.disabled = True
    
    def delete_motor(self, _):
        """Delete the selected motor"""
        if not self.current_motor_id:
            return
        
        motors = self.controller.get_motors()
        motor = next((m for m in motors if m.get('uniqueID') == self.current_motor_id), None)
        
        if motor:
            motor_name = motor.get('name')
            
            # Remove the motor from all MCUs first
            mcus = self.controller.get_mcus()
            for mcu in mcus:
                if 'motors' in mcu:
                    original_length = len(mcu['motors'])
                    mcu['motors'] = [m for m in mcu['motors'] if m.get('uniqueID') != self.current_motor_id]
                    if len(mcu['motors']) != original_length:
                        self.controller.profile_manager.update_mcu(mcu)
            
            # Now delete the motor profile
            motors = [m for m in motors if m.get('uniqueID') != self.current_motor_id]
            self.controller.profile_manager.save_motors(motors)
            self.log(f"Deleted motor: {motor_name}", clear=True)
            self.refresh_mcus()
            self.refresh_motors()
            
            # Reset the edit fields
            self.current_motor_id = None
            self.edit_motor_name.value = ''
            self.edit_motor_step_pin.value = 0
            self.edit_motor_dir_pin.value = 0
            self.edit_motor_name.disabled = True
            self.edit_motor_step_pin.disabled = True
            self.edit_motor_dir_pin.disabled = True
            self.save_motor_button.disabled = True
            self.delete_motor_button.disabled = True
    
    def configure_pins(self, _):
        """Configure the step and dir pins for the selected motor in an MCU"""
        # We now get the selected motor from the calibration_motor_dropdown
        selected_motor = self.selected_motor
        selected_mcu = self.selected_mcu
        
        if not self.selected_port:
            self.log("Please connect to a port first", clear=True)
            return
            
        if not selected_mcu:
            self.log("No MCU available for this motor. Configure the motor in an MCU first.", clear=True)
            return
            
        if not selected_motor:
            self.log("Please select a motor profile first", clear=True)
            return
        
        step_pin = self.step_pin_input.value
        dir_pin = self.dir_pin_input.value
        
        self.log(f"Configuring pins for {selected_motor['name']} in {selected_mcu['name']}...", clear=True)
        
        # Find the motor in the MCU
        motor_in_mcu = None
        for motor in selected_mcu.get('motors', []):
            if motor.get('uniqueID') == selected_motor.get('uniqueID'):
                motor_in_mcu = motor
                break
        
        # Update or add the motor to the MCU
        if motor_in_mcu:
            motor_in_mcu['step'] = step_pin
            motor_in_mcu['dir'] = dir_pin
        else:
            if 'motors' not in selected_mcu:
                selected_mcu['motors'] = []
                
            selected_mcu['motors'].append({
                'uniqueID': selected_motor.get('uniqueID'),
                'name': selected_motor.get('name'),
                'step': step_pin,
                'dir': dir_pin
            })
        
        # Save the updated MCU profile
        self.controller.profile_manager.update_mcu(selected_mcu)
        self.log(f"Motor pins configured successfully: step={step_pin}, dir={dir_pin}")
        
        # Update the step and dir pins for future operations
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        
        # Update the MCU info display
        self.calibration_mcu_info.value = (
            f"<p>Using MCU: <b>{self.selected_mcu.get('name')}</b> with "
            f"Step Pin: <b>{self.step_pin}</b>, Dir Pin: <b>{self.dir_pin}</b></p>"
        )
        
        # Refresh the MCU list to show the updated configuration
        self.display_mcu_list()
    
    def run_first_trial(self, _):
        """Run the first calibration trial"""
        self.run_calibration_trial("First")
    
    def run_second_trial(self, _):
        """Run the second calibration trial"""
        self.run_calibration_trial("Second")
    
    def calculate_calibration(self, _):
        """Calculate the calibration parameters based on trial data"""
        # Update selections from dropdowns
        self.update_selected_items()
        
        if not self.selected_motor:
            self.log("Please select a motor profile first", clear=True)
            return
        
        # Check for required syringe information
        syringe_brand = self.syringe_brand_input.value.strip()
        syringe_model = self.syringe_model_input.value.strip()
        syringe_volume = self.syringe_volume_input.value
        syringe_diameter = self.syringe_diameter_input.value
        
        if not syringe_brand or not syringe_model:
            self.log("Please enter syringe brand and model information", clear=True)
            return
        
        if syringe_volume <= 0 or syringe_diameter <= 0:
            self.log("Please enter valid syringe volume and diameter values", clear=True)
            return
        
        # Get measurement values from input fields
        first_measurement = self.first_trial_measurement_input.value
        second_measurement = self.second_trial_measurement_input.value
        
        if first_measurement <= 0 or second_measurement <= 0:
            self.log("Please enter valid measurements for both trials", clear=True)
            return
        
        # Store trial data and convert to mL/min
        self.first_trial = {
            "freq": self.first_trial_freq_input.value,
            "duration": self.first_trial_duration_input.value,
            "measurement": first_measurement,
            "ups": (first_measurement / self.first_trial_duration_input.value) * 60  # Convert to mL/min
        }
        
        self.second_trial = {
            "freq": self.second_trial_freq_input.value,
            "duration": self.second_trial_duration_input.value,
            "measurement": second_measurement,
            "ups": (second_measurement / self.second_trial_duration_input.value) * 60  # Convert to mL/min
        }
        
        self.log(f"Calculating calibration parameters...", clear=True)
        
        # Calculate calibration parameters
        ups_slope = (self.second_trial["ups"] - self.first_trial["ups"]) / (self.second_trial["freq"] - self.first_trial["freq"])
        ups_intercept = self.first_trial["ups"] - ups_slope * self.first_trial["freq"]
        
        max_ups = ups_intercept + ups_slope * 1000  # Cap at x=1000Hz
        min_ups = ups_intercept  # Bottom at 0Hz
        if min_ups < 0.000005:
            min_ups = 0.000005  # Minimum threshold
        
        # Update the motor profile with calibration data
        self.selected_motor["UPSSlope"] = ups_slope
        self.selected_motor["UPSIntercept"] = ups_intercept
        self.selected_motor["maxUPS"] = max_ups
        self.selected_motor["minUPS"] = min_ups
        self.selected_motor["calibrated"] = True
        
        # Add syringe information to the motor profile
        self.selected_motor["syringeInfo"] = {
            "brand": syringe_brand,
            "model": syringe_model,
            "volumeML": syringe_volume,
            "innerDiameterMM": syringe_diameter,  # Changed key name to innerDiameterMM
            "calibrationDate": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save the updated motor profile
        self.controller.profile_manager.update_motor(self.selected_motor)
        
        # Display the results
        with self.calibration_results:
            clear_output()
            print(f"Calibration calculation complete:")
            print(f"Flow Rate Slope: {ups_slope:.6f}")
            print(f"Flow Rate Intercept: {ups_intercept:.6f}")
            print(f"Min Flow Rate: {min_ups:.6f} mL/min")
            print(f"Max Flow Rate: {max_ups:.2f} mL/min")
            print(f"\nCalibrated with:")
            print(f"Syringe Brand: {syringe_brand}")
            print(f"Syringe Model: {syringe_model}")
            print(f"Syringe Volume: {syringe_volume} mL")
            print(f"Syringe Inner Diameter: {syringe_diameter} mm")  # Updated text
            
        self.log(f"Calibration saved successfully", clear=True)
        
        # Update test widget range
        self.test_ups_input.min = min_ups
        self.test_ups_input.max = max_ups
    
    def run_test(self, _):
        """Test a calibrated motor at a specific UPS"""
        # Get selections from test dropdowns
        selected_mcu = self.test_mcu_dropdown.value
        selected_motor = self.test_motor_dropdown.value
        
        if not self.selected_port:
            self.log("Please connect to a port first", clear=True)
            return
            
        if not selected_mcu:
            self.log("Please select an MCU profile first", clear=True)
            return
            
        if not selected_motor:
            self.log("Please select a motor profile first", clear=True)
            return
            
        if not selected_motor.get("calibrated"):
            self.log("Motor is not calibrated! Please calibrate it first.", clear=True)
            return
        
        # Get test parameters
        ups = self.test_ups_input.value
        direction = self.test_direction.value
        duration = self.test_duration_input.value
        custom_diameter = self.test_syringe_diameter.value if not self.test_use_calibrated_checkbox.value else 0.0
        
        # Get calibration parameters
        min_ups = selected_motor.get("minUPS", 0)
        max_ups = selected_motor.get("maxUPS", 0)
        
        # Validate UPS
        if ups < min_ups:
            self.log(f"Speed too low! Minimum is {min_ups:.6f} mL/min", clear=True)
            return
            
        if ups > max_ups:
            self.log(f"Speed too high! Maximum is {max_ups:.2f} mL/min", clear=True)
            return
        
        self.log(f"Running motor at {ups} mL/min {direction} for {duration} seconds...", clear=True)
        
        # First stop any running motor to clear buffer and ensure clean state
        self.controller.stop_command(self.selected_port, selected_mcu, selected_motor)
        time.sleep(0.5)  # Give time for stop command to process
        
        # Find the motor in the MCU profile to get pins
        motor_config = None
        for motor in selected_mcu.get('motors', []):
            if motor.get('uniqueID') == selected_motor.get('uniqueID'):
                motor_config = motor
                break
                
        if not motor_config:
            self.log("Error: Motor not found in MCU profile", clear=True)
            return
            
        # Get step and dir pins
        step_pin = motor_config.get("step")
        dir_pin = motor_config.get("dir")
        
        # Convert UPS to frequency
        freq = self.controller.command_processor.convert_ups_to_freq(selected_motor, ups)
        if freq is None:
            return
            
        # Round frequency to integer for stepper motor
        freq_int = int(round(freq))
        self.log(f"Using calculated frequency: {freq:.2f}Hz (rounded to {freq_int}Hz for stepper motor)", clear=False)
        
        # Create command with syringe info if available
        command = {
            "type": "timed",
            "direction": direction,
            "freq": freq_int,  # Use integer frequency
            "stepPin": int(step_pin),  # Ensure integer values
            "dirPin": int(dir_pin),    # Ensure integer values
            "timeValue": float(duration),
            "timeUnit": "s"
        }
        
        # Handle custom syringe diameter if provided
        if custom_diameter > 0.0:
            command["syringeDiameter"] = float(custom_diameter)  # Ensure proper float formatting
            self.log(f"Using custom syringe inner diameter: {custom_diameter}mm", clear=False)
            
            # If there's calibrated diameter info, provide it as reference
            if "syringeInfo" in selected_motor:
                si = selected_motor["syringeInfo"]
                if "innerDiameterMM" in si:
                    command["referenceDiameter"] = si.get("innerDiameterMM")
                elif "diameterMM" in si:
                    command["referenceDiameter"] = si.get("diameterMM")
        # Add calibrated syringe diameter if available and not using custom
        elif "syringeInfo" in selected_motor:
            si = selected_motor["syringeInfo"]
            if "innerDiameterMM" in si:
                command["syringeDiameter"] = si.get("innerDiameterMM")
                self.log(f"Using calibrated syringe inner diameter: {si.get('innerDiameterMM')}mm", clear=False)
            elif "diameterMM" in si:
                command["syringeDiameter"] = si.get("diameterMM")
                self.log(f"Using calibrated syringe diameter: {si.get('diameterMM')}mm", clear=False)
        
        # Send the command directly
        success = self.controller.serial_manager.send_command(self.selected_port, command)
        
        if success:
            self.log(f"Sent command to {self.selected_port}: timed run at {freq}Hz for {duration}s", clear=False)
            
            # Start a countdown timer
            for remaining in range(int(duration), 0, -1):
                self.log(f"Running... {remaining}s remaining", clear=True)
                time.sleep(1)
                
            # Stop the motor after the test to ensure it's not left running
            self.controller.stop_command(self.selected_port, selected_mcu, selected_motor)
            time.sleep(0.5)  # Give time for stop command to process
                
            self.log(f"Test complete!", clear=True)
        else:
            self.log(f"Error running the motor!", clear=True)
    
    def stop_motor(self, _):
        """Stop the motor"""
        # Get selections from test dropdowns
        selected_mcu = self.test_mcu_dropdown.value
        selected_motor = self.test_motor_dropdown.value
        
        if not self.selected_port or not selected_mcu or not selected_motor:
            self.log("Please select port, MCU and motor first", clear=True)
            return
            
        self.log("Stopping motor...", clear=True)
        
        success = self.controller.stop_command(self.selected_port, selected_mcu, selected_motor)
        
        if success:
            self.log("Motor stopped", clear=True)
        else:
            self.log("Failed to stop motor", clear=True)
    
    def cleanup(self):
        """Clean up resources when done"""
        # Stop any running motors before cleanup
        if self.selected_port and self.selected_mcu and self.selected_motor:
            self.controller.stop_command(self.selected_port, self.selected_mcu, self.selected_motor)
            time.sleep(0.5)  # Give time for stop command to process
            
        # Close all ports properly
        if self.selected_port:
            self.controller.disconnect_port(self.selected_port)
            self.selected_port = None
            self.disconnect_button.disabled = True
        
        # Clean up controller resources
        self.controller.cleanup()
        self.log("Resources cleaned up", clear=True)
        
    def __del__(self):
        """Destructor to ensure cleanup when the object is garbage collected"""
        try:
            self.cleanup()
        except:
            pass

    def update_selected_items(self):
        """Update the selected items from dropdowns"""
        if self.calibration_motor_dropdown.value:
            self.selected_motor = self.calibration_motor_dropdown.value
                
        # Check if this motor is already in the MCU and update pin fields if so
        if self.selected_mcu and self.selected_motor and 'motors' in self.selected_mcu:
            for motor in self.selected_mcu['motors']:
                if motor.get('uniqueID') == self.selected_motor.get('uniqueID'):
                    self.step_pin_input.value = motor.get('step', 0)
                    self.dir_pin_input.value = motor.get('dir', 0)
                    break

    def update_test_selections(self, change):
        """Update the available motors when an MCU is selected in the test tab"""
        if change['new'] is None:
            self.test_motor_dropdown.options = [('Select Motor', None)]
            with self.test_calibration_details:
                clear_output()
                print("No motor selected.")
            return
                
        selected_mcu = change['new']
        
        # Get all motors
        motors = self.controller.get_motors()
        
        # Filter motors based on if they're configured in this MCU and calibrated
        mcu_motor_ids = [motor.get('uniqueID') for motor in selected_mcu.get('motors', [])]
        calibrated_motors = [motor for motor in motors if motor.get('uniqueID') in mcu_motor_ids and motor.get('calibrated')]
        
        # Update the test motor dropdown
        self.test_motor_dropdown.options = [('Select Motor', None)] + [(motor['name'], motor) for motor in calibrated_motors]
        
        # Reset the motor selection
        self.test_motor_dropdown.value = None
        
        # Clear calibration details
        with self.test_calibration_details:
            clear_output()
            print("Select a calibrated motor to view details.")
    
    def update_calibration_details(self):
        """Update the calibration details display based on current selections"""
        # Clear the current display
        with self.test_calibration_details:
            clear_output()
            
            # Get the selected motor
            selected_motor = self.test_motor_dropdown.value
            if not selected_motor:
                print("No motor selected.")
                return
            
            # Get the current flow rate and custom diameter settings
            flow_rate = self.test_ups_input.value
            custom_diameter = self.test_syringe_diameter.value if not self.test_use_calibrated_checkbox.value else 0.0
            
            # Display calibration parameters
            print(f"=== Motor: {selected_motor.get('name')} ===")
            
            # Show calibration parameters
            slope = selected_motor.get("UPSSlope", 0)
            intercept = selected_motor.get("UPSIntercept", 0)
            min_ups = selected_motor.get("minUPS", 0)
            max_ups = selected_motor.get("maxUPS", 0)
            print(f"Calibration Parameters:")
            print(f"  - Slope: {slope:.6f}")
            print(f"  - Intercept: {intercept:.6f}")
            print(f"  - Flow Rate Range: {min_ups:.6f} to {max_ups:.2f} mL/min")
            
            # Show original syringe info
            if "syringeInfo" in selected_motor:
                si = selected_motor["syringeInfo"]
                cal_date = si.get("calibrationDate", "Unknown")
                
                # Get diameter and use correct key
                if "innerDiameterMM" in si:
                    calibrated_diameter = si.get("innerDiameterMM")
                    diameter_label = "Inner Diameter"
                else:
                    calibrated_diameter = si.get("diameterMM")
                    diameter_label = "Diameter"
                    
                print(f"\nCalibrated with:")
                print(f"  - Syringe: {si.get('brand')} {si.get('model')}")
                print(f"  - Volume: {si.get('volumeML')}mL, {diameter_label}: {calibrated_diameter}mm")
                print(f"  - Calibration Date: {cal_date}")
                
                # Calculate base frequency
                freq = self.controller.command_processor.convert_ups_to_freq(selected_motor, flow_rate)
                freq_int = int(round(freq)) if freq is not None else 0
                
                print(f"\nCurrent Settings:")
                print(f"  - Flow Rate: {flow_rate:.4f} mL/min")
                print(f"  - Base Frequency: {freq:.2f}Hz ({freq_int}Hz rounded)")
                
                # Show the effect of custom diameter if specified
                if custom_diameter > 0.0:
                    ratio = (calibrated_diameter / custom_diameter) ** 2
                    adjusted_freq = freq_int * ratio if freq is not None else 0
                    
                    print(f"\nCustom Syringe Calculations:")
                    print(f"  - Custom Inner Diameter: {custom_diameter}mm")
                    print(f"  - Calibrated Diameter: {calibrated_diameter}mm")
                    print(f"  - Area Ratio: {ratio:.4f} (calibrated/custom)²") 
                    print(f"  - Frequency Adjustment: {freq_int}Hz → {int(round(adjusted_freq))}Hz")
                    
                    # Explain what this means
                    if ratio > 1:
                        print(f"  - Effect: Motor will run FASTER to maintain flow rate")
                        print(f"    (Custom syringe is narrower than calibrated syringe)")
                    else:
                        print(f"  - Effect: Motor will run SLOWER to maintain flow rate")
                        print(f"    (Custom syringe is wider than calibrated syringe)")
    
    def test_motor_dropdown_changed(self, change):
        """Handle when the test motor dropdown value changes"""
        if change['new'] is None:
            with self.test_calibration_details:
                clear_output()
                print("No motor selected.")
            return
        
        # Update details display
        self.update_calibration_details()
        
        # Update syringe diameter placeholder
        selected_motor = change['new']
        if selected_motor and "syringeInfo" in selected_motor:
            si = selected_motor["syringeInfo"]
            if "innerDiameterMM" in si:
                diameter = si.get("innerDiameterMM")
                label = "inner diameter"
            else:
                diameter = si.get("diameterMM")
                label = "diameter"
                
            # Set the tooltip or placeholder to show what diameter is calibrated
            self.test_syringe_diameter.placeholder = f"Calibrated: {diameter}mm"
    
    def toggle_diameter_field(self, change):
        """Enable or disable the custom syringe diameter input based on checkbox"""
        self.test_syringe_diameter.disabled = change['new']
        if change['new']:  # if using calibrated data
            self.test_syringe_diameter.value = 0.0
        
        # Update calibration details display
        self.update_calibration_details()
    
    def update_flow_rate(self, change):
        """Update calculations when flow rate changes"""
        self.update_calibration_details()
    
    def update_custom_diameter(self, change):
        """Update calculations when custom diameter changes"""
        self.update_calibration_details()
    
    def find_mcu_for_motor(self, motor_id):
        """Find an MCU that has the specified motor configured and connected"""
        if not motor_id or not self.selected_port:
            return None
            
        # Get all MCU profiles
        mcus = self.controller.get_mcus()
        
        # First look for any MCU that has this motor configured
        for mcu in mcus:
            for motor in mcu.get('motors', []):
                if motor.get('uniqueID') == motor_id:
                    return mcu
        
        return None

    def calibration_motor_changed(self, change):
        """Handle motor selection change in the calibration tab"""
        selected_motor = change.new
        
        if not selected_motor:
            self.calibration_mcu_info.value = "<p>No motor selected</p>"
            return
        
        # Store the selected motor
        self.selected_motor = selected_motor
        
        # Find an MCU with this motor
        self.selected_mcu = self.find_mcu_for_motor(selected_motor.get('uniqueID'))
        
        if not self.selected_mcu:
            self.calibration_mcu_info.value = (
                f"<p style='color: red;'>Motor '{selected_motor.get('name')}' is not configured in any MCU. "
                f"Please go to the Motor Profiles tab and associate this motor with an MCU.</p>"
            )
            self.run_first_trial_button.disabled = True
            self.run_second_trial_button.disabled = True
            return
        
        # Find motor configuration in the MCU
        motor_config = None
        for motor in self.selected_mcu.get('motors', []):
            if motor.get('uniqueID') == selected_motor.get('uniqueID'):
                motor_config = motor
                break
        
        if not motor_config:
            self.calibration_mcu_info.value = "<p style='color: red;'>Motor configuration not found.</p>"
            self.run_first_trial_button.disabled = True
            self.run_second_trial_button.disabled = True
            return
        
        # Store pin configuration
        self.step_pin = motor_config.get('step', 0)
        self.dir_pin = motor_config.get('dir', 0)
        
        # Update info display
        self.calibration_mcu_info.value = (
            f"<p>Using MCU: <b>{self.selected_mcu.get('name')}</b> with "
            f"Step Pin: <b>{self.step_pin}</b>, Dir Pin: <b>{self.dir_pin}</b></p>"
        )
        
        # Fill in existing syringe info if available
        if "syringeInfo" in selected_motor:
            si = selected_motor["syringeInfo"]
            self.syringe_brand_input.value = si.get('brand', '')
            self.syringe_model_input.value = si.get('model', '')
            self.syringe_volume_input.value = si.get('volumeML', 10.0)
            
            # Handle both old and new diameter key names
            if "innerDiameterMM" in si:
                self.syringe_diameter_input.value = si.get('innerDiameterMM', 15.0)
                diameter_label = "inner dia"
                diameter_value = si.get('innerDiameterMM')
            else:
                self.syringe_diameter_input.value = si.get('diameterMM', 15.0)
                diameter_label = "dia"
                diameter_value = si.get('diameterMM')
            
            # Add additional info to the display
            self.calibration_mcu_info.value += (
                f"<p>Previously calibrated with: <b>{si.get('brand')} {si.get('model')}</b> "
                f"({si.get('volumeML')}mL, {diameter_value}mm {diameter_label}) on {si.get('calibrationDate', 'Unknown')}</p>"
            )
        else:
            # Reset syringe fields if no prior calibration
            self.syringe_brand_input.value = ''
            self.syringe_model_input.value = ''
            self.syringe_volume_input.value = 10.0
            self.syringe_diameter_input.value = 15.0
        
        # Enable run buttons
        self.run_first_trial_button.disabled = False
        self.run_second_trial_button.disabled = False

    def update_association_dropdowns(self):
        """Update the association dropdowns with current motors and MCUs"""
        # Update motor dropdown
        motors = self.controller.get_motors()
        self.associate_motor_dropdown.options = [('Select Motor', None)] + [(motor['name'], motor) for motor in motors]
        
        # Update MCU dropdown
        mcus = self.controller.get_mcus()
        self.associate_mcu_dropdown.options = [('Select MCU', None)] + [(mcu['name'], mcu) for mcu in mcus]
    
    def associate_motor_with_mcu(self, _):
        """Associate a motor with an MCU"""
        selected_motor = self.associate_motor_dropdown.value
        selected_mcu = self.associate_mcu_dropdown.value
        
        if not selected_motor:
            self.log("Please select a motor first", clear=True)
            return
            
        if not selected_mcu:
            self.log("Please select an MCU first", clear=True)
            return
        
        step_pin = self.associate_step_pin.value
        dir_pin = self.associate_dir_pin.value
        
        self.log(f"Associating motor '{selected_motor['name']}' with MCU '{selected_mcu['name']}'...", clear=True)
        
        # Find the motor in the MCU
        motor_in_mcu = None
        for motor in selected_mcu.get('motors', []):
            if motor.get('uniqueID') == selected_motor.get('uniqueID'):
                motor_in_mcu = motor
                break
        
        # Update or add the motor to the MCU
        if motor_in_mcu:
            motor_in_mcu['step'] = step_pin
            motor_in_mcu['dir'] = dir_pin
            self.log(f"Updated existing motor association with step={step_pin}, dir={dir_pin}")
        else:
            if 'motors' not in selected_mcu:
                selected_mcu['motors'] = []
                
            selected_mcu['motors'].append({
                'uniqueID': selected_motor.get('uniqueID'),
                'name': selected_motor.get('name'),
                'step': step_pin,
                'dir': dir_pin
            })
            self.log(f"Created new motor association with step={step_pin}, dir={dir_pin}")
        
        # Save the updated MCU profile
        self.controller.profile_manager.update_mcu(selected_mcu)
        self.log(f"Motor '{selected_motor['name']}' successfully associated with MCU '{selected_mcu['name']}'")
        
        # Refresh displays
        self.display_mcu_list()
        self.display_motor_list()
        
        # After successful association, update the edit motor screen if it's showing the same motor
        if self.current_motor_id == selected_motor.get('uniqueID'):
            self.edit_motor(self.current_motor_id)

# Usage example:
# In a Jupyter notebook, do the following:
# 
# from jupyter_calibration import JupyterCalibrationTool
# tool = JupyterCalibrationTool()
#
# When done:
# tool.cleanup()