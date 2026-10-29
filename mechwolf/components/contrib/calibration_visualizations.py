import ipywidgets as widgets
from IPython.display import clear_output, display, HTML
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import graphviz
from datetime import datetime

class CalibrationVisualizer:
    """Class to visualize calibration data and MCU-motor relationships"""
    
    def __init__(self, controller):
        """Initialize the visualizer with a reference to the FreeStepController"""
        self.controller = controller
        self.create_widgets()
        
    def create_widgets(self):
        """Create all widgets for the visualization tab"""
        # Motor profile selection for calibration plot
        self.motor_dropdown = widgets.Dropdown(
            description='Select Motor:',
            options=[],
            layout=widgets.Layout(width='50%')
        )
        self.refresh_motors_button = widgets.Button(
            description='Refresh Motors',
            button_style='info',
            icon='refresh'
        )
        self.generate_plot_button = widgets.Button(
            description='Generate Plot',
            button_style='success',
            icon='chart-line'
        )
        self.calibration_plot_output = widgets.Output(
            layout={'border': '1px solid #ddd', 'padding': '10px', 'height': '600px'}
        )
        
        # Diameter comparison widgets
        self.diameter_comparison_title = widgets.HTML("<h3>Syringe Diameter Comparison</h3>")
        self.diameter_comparison_description = widgets.HTML(
            "<p>Compare how flow rates change when using different syringe diameters</p>"
        )
        self.diameter_motor_dropdown = widgets.Dropdown(
            description='Select Motor:',
            options=[],
            layout=widgets.Layout(width='50%')
        )
        self.new_diameter_input = widgets.FloatText(
            description='New Inner Diameter (mm):',
            value=0.0,
            min=0.1,
            step=0.1,
            layout=widgets.Layout(width='50%')
        )
        self.generate_diameter_plot_button = widgets.Button(
            description='Compare Diameters',
            button_style='success',
            icon='chart-line'
        )
        self.diameter_plot_output = widgets.Output(
            layout={'border': '1px solid #ddd', 'padding': '10px', 'height': '800px', 'overflow': 'auto'}
        )
        
        # GraphViz visualization
        self.generate_graph_button = widgets.Button(
            description='Generate MCU-Motor Graph',
            button_style='success',
            icon='project-diagram'
        )
        self.graph_output = widgets.Output(
            layout={'border': '1px solid #ddd', 'padding': '10px', 'height': '500px', 'overflow': 'auto'}
        )
        
        # Add button event handlers
        self.refresh_motors_button.on_click(self.refresh_motors)
        self.generate_plot_button.on_click(self.generate_calibration_plot)
        self.generate_graph_button.on_click(self.generate_mcu_motor_graph)
        self.generate_diameter_plot_button.on_click(self.generate_diameter_comparison_plot)
        
        # Initial data load
        self.refresh_motors()
    
    def refresh_motors(self, _=None):
        """Refresh the available motor profiles, focusing on calibrated ones"""
        motors = self.controller.get_motors()
        
        # Filter for calibrated motors
        calibrated_motors = [motor for motor in motors if motor.get('calibrated')]
        
        # Update motor dropdowns
        self.motor_dropdown.options = [('Select Motor', None)] + [(motor['name'], motor) for motor in calibrated_motors]
        self.diameter_motor_dropdown.options = [('Select Motor', None)] + [(motor['name'], motor) for motor in calibrated_motors]
        self.motor_dropdown.value = None
        self.diameter_motor_dropdown.value = None
        
        # Clear any existing plots
        with self.calibration_plot_output:
            clear_output()
            if not calibrated_motors:
                print("No calibrated motors found. Please calibrate a motor first.")
            else:
                print("Select a calibrated motor and click 'Generate Plot'.")
                
        with self.diameter_plot_output:
            clear_output()
            if not calibrated_motors:
                print("No calibrated motors found. Please calibrate a motor first.")
            else:
                print("Select a calibrated motor, enter a new diameter, and click 'Compare Diameters'.")
    
    def generate_calibration_plot(self, _=None):
        """Generate a plot showing the calibration curve for the selected motor"""
        selected_motor = self.motor_dropdown.value
        
        if not selected_motor:
            with self.calibration_plot_output:
                clear_output()
                print("Please select a calibrated motor first.")
            return
        
        # Get calibration parameters
        slope = selected_motor.get("UPSSlope", 0)
        intercept = selected_motor.get("UPSIntercept", 0)
        min_ups = selected_motor.get("minUPS", 0)
        max_ups = selected_motor.get("maxUPS", 0)
        
        with self.calibration_plot_output:
            clear_output()
            
            # Create the figure with increased size and bottom margin
            fig = plt.figure(figsize=(10, 7))  # Increased height from 6 to 7
            ax = fig.add_subplot(111)
            
            # Generate x values (frequency in Hz)
            x = np.linspace(0, 1000, 1000)
            
            # Calculate corresponding flow rates (mL/min)
            y = slope * x + intercept
            
            # Plot the calibration line
            ax.plot(x, y, 'b-', linewidth=2, label='Calibration Curve')
            
            # Mark the valid range
            min_freq = (min_ups - intercept) / slope if slope != 0 else 0
            max_freq = 1000  # Cap at 1000 Hz
            
            # Highlight the valid range
            ax.axvspan(min_freq, max_freq, alpha=0.2, color='green', label='Valid Frequency Range')
            ax.axhspan(min_ups, max_ups, alpha=0.1, color='blue', label='Valid Flow Rate Range')
            
            # Add markers for min and max values
            ax.plot([min_freq], [min_ups], 'ro', markersize=8, label=f'Min: {min_ups:.6f} mL/min @ {min_freq:.1f} Hz')
            ax.plot([max_freq], [max_ups], 'go', markersize=8, label=f'Max: {max_ups:.2f} mL/min @ {max_freq:.1f} Hz')
            
            # Get syringe info if available
            syringe_info = ""
            if "syringeInfo" in selected_motor:
                si = selected_motor["syringeInfo"]
                brand = si.get("brand", "Unknown")
                model = si.get("model", "Unknown")
                volume = si.get("volumeML", 0)
                
                # Check which diameter key exists
                if "innerDiameterMM" in si:
                    diameter = si.get("innerDiameterMM", 0)
                    diameter_label = "inner diameter"
                else:
                    diameter = si.get("diameterMM", 0)
                    diameter_label = "diameter"
                    
                cal_date = si.get("calibrationDate", "Unknown")
                syringe_info = f"\nCalibrated with: {brand} {model} {volume}mL ({diameter}mm {diameter_label}) on {cal_date}"
            
            # Set titles and labels with increased fontsize
            ax.set_title(f'Calibration Curve for {selected_motor.get("name")}{syringe_info}', fontsize=12)
            ax.set_xlabel('Frequency (Hz)', fontsize=12)
            ax.set_ylabel('Flow Rate (mL/min)', fontsize=12)
            
            # Increase tick label size
            ax.tick_params(axis='both', which='major', labelsize=10)
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Add formula text
            formula = f"Flow Rate = {slope:.6f} × Frequency + {intercept:.6f}"
            ax.text(0.05, 0.95, formula, transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            # Add legend
            ax.legend(loc='lower right')
            
            # Adjust limits
            ax.set_xlim(0, max_freq * 1.05)
            ax.set_ylim(0, max_ups * 1.05)
            
            # Apply tight layout with increased padding
            plt.tight_layout(pad=3.0, h_pad=None, w_pad=None, rect=[0, 0.08, 1, 0.95])  # Increased bottom padding
            
            # Add more space at the bottom explicitly
            plt.subplots_adjust(bottom=0.18)  # Increased from 0.15 to 0.18
            
            plt.show()
    
    def generate_diameter_comparison_plot(self, _=None):
        """Generate a plot comparing flow rates with different syringe diameters"""
        selected_motor = self.diameter_motor_dropdown.value
        new_diameter = self.new_diameter_input.value
        
        if not selected_motor:
            with self.diameter_plot_output:
                clear_output()
                print("Please select a calibrated motor first.")
            return
        
        if new_diameter <= 0:
            with self.diameter_plot_output:
                clear_output()
                print("Please enter a valid new diameter (greater than 0).")
            return
        
        # Get calibration parameters
        slope = selected_motor.get("UPSSlope", 0)
        intercept = selected_motor.get("UPSIntercept", 0)
        min_ups = selected_motor.get("minUPS", 0)
        max_ups = selected_motor.get("maxUPS", 0)
        
        # Get original syringe diameter
        original_diameter = None
        diameter_label = "diameter"
        
        if "syringeInfo" in selected_motor:
            si = selected_motor["syringeInfo"]
            # Check which diameter key exists
            if "innerDiameterMM" in si:
                original_diameter = si.get("innerDiameterMM", 0)
                diameter_label = "inner diameter"
            else:
                original_diameter = si.get("diameterMM", 0)
                diameter_label = "diameter"
        
        if not original_diameter:
            with self.diameter_plot_output:
                clear_output()
                print("Error: Could not find original syringe diameter in motor calibration data.")
            return
        
        with self.diameter_plot_output:
            clear_output()
            
            # Create the figure with adjusted height - slightly smaller to leave room for analysis
            fig = plt.figure(figsize=(12, 7.5))  # Reduced from 9 to 7.5 to leave space for analysis
            ax = fig.add_subplot(111)
            
            # Generate x values (frequency in Hz)
            x = np.linspace(0, 1000, 1000)
            
            # Calculate flow rates for original diameter
            original_flow_rates = slope * x + intercept
            
            # Calculate flow rates for new diameter using the mathematical relationship:
            # new_flow = original_flow * (new_diameter/original_diameter)²
            diameter_ratio_squared = (new_diameter / original_diameter) ** 2
            new_flow_rates = original_flow_rates * diameter_ratio_squared
            
            # Calculate the new min and max flow rates
            new_min_ups = min_ups * diameter_ratio_squared
            new_max_ups = max_ups * diameter_ratio_squared
            
            # Find new frequency boundaries
            # Solve flow_rate = slope * freq + intercept for freq
            # freq = (flow_rate - intercept) / slope
            new_min_freq = (new_min_ups - intercept) / slope if slope != 0 else 0
            
            # Plot both calibration curves
            ax.plot(x, original_flow_rates, 'b-', linewidth=2, 
                   label=f'Original ({original_diameter}mm {diameter_label})')
            ax.plot(x, new_flow_rates, 'r-', linewidth=2, 
                   label=f'New ({new_diameter}mm {diameter_label})')
            
            # Mark original valid range
            ax.axhspan(min_ups, max_ups, alpha=0.1, color='blue', 
                      label=f'Original Valid Range: {min_ups:.6f} - {max_ups:.2f} mL/min')
            
            # Mark new valid range
            ax.axhspan(new_min_ups, new_max_ups, alpha=0.1, color='red', 
                      label=f'New Valid Range: {new_min_ups:.6f} - {new_max_ups:.2f} mL/min')
            
            # Add markers for min and max values
            min_freq = (min_ups - intercept) / slope if slope != 0 else 0
            max_freq = 1000  # Cap at 1000 Hz
            
            ax.plot([min_freq], [min_ups], 'bo', markersize=8)
            ax.plot([max_freq], [max_ups], 'bo', markersize=8)
            ax.plot([new_min_freq], [new_min_ups], 'ro', markersize=8)
            ax.plot([max_freq], [new_max_ups], 'ro', markersize=8)
            
            # Set titles and labels
            ax.set_title(f'Diameter Comparison for {selected_motor.get("name")}', fontsize=14)
            ax.set_xlabel('Frequency (Hz)', fontsize=12)
            ax.set_ylabel('Flow Rate (mL/min)', fontsize=12)
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Add mathematical explanation - moved to bottom right corner
            explanation = (
                f"Flow Rate Ratio = (New Diameter / Original Diameter)²\n"
                f"Flow Rate Ratio = ({new_diameter:.2f} / {original_diameter:.2f})² = {diameter_ratio_squared:.4f}\n"
                f"New Flow Rate = Original Flow Rate × {diameter_ratio_squared:.4f}"
            )
            ax.text(0.95, 0.05, explanation, transform=ax.transAxes, fontsize=12,
                   verticalalignment='bottom', horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            # Add legend - moved to upper left to avoid overlap with formula
            ax.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98))
            
            # Adjust limits to show both curves
            max_y = max(max_ups, new_max_ups) * 1.1
            ax.set_xlim(0, 1050)
            ax.set_ylim(0, max_y)
            
            # Apply tight layout with increased padding
            plt.tight_layout(pad=3.0, rect=[0, 0.08, 1, 0.95])  # Added rect parameter to increase bottom margin
            
            # Add more space at the bottom explicitly
            plt.subplots_adjust(bottom=0.18)
            
            plt.show()
            
            # Add additional explanation text with more visible styling
            if diameter_ratio_squared > 1:
                display(HTML(
                    f"<div style='background-color: #f8f8f8; padding: 15px; margin-top: 20px; border-left: 5px solid #2196F3; border-radius: 4px;'>"
                    f"<h3 style='margin-top: 0;'>Analysis Results</h3>"
                    f"<p><b>Analysis:</b> With a {new_diameter}mm diameter syringe (compared to the original {original_diameter}mm):</p>"
                    f"<p>• Flow rates are <b>increased</b> by a factor of {diameter_ratio_squared:.4f}</p>"
                    f"<p>• This is because the cross-sectional area is larger (Area ∝ Diameter²)</p>"
                    f"<p>• At the same motor frequency, you'll get {diameter_ratio_squared:.2f}× more volume output</p>"
                    f"<p>• To maintain the same flow rate as the original calibration, reduce the frequency by {100*(1-1/diameter_ratio_squared):.1f}%</p>"
                    f"</div>"
                ))
            else:
                display(HTML(
                    f"<div style='background-color: #f8f8f8; padding: 15px; margin-top: 20px; border-left: 5px solid #2196F3; border-radius: 4px;'>"
                    f"<h3 style='margin-top: 0;'>Analysis Results</h3>"
                    f"<p><b>Analysis:</b> With a {new_diameter}mm diameter syringe (compared to the original {original_diameter}mm):</p>"
                    f"<p>• Flow rates are <b>decreased</b> by a factor of {diameter_ratio_squared:.4f}</p>"
                    f"<p>• This is because the cross-sectional area is smaller (Area ∝ Diameter²)</p>"
                    f"<p>• At the same motor frequency, you'll get {diameter_ratio_squared:.2f}× less volume output</p>"
                    f"<p>• To maintain the same flow rate as the original calibration, increase the frequency by {100*(1/diameter_ratio_squared-1):.1f}%</p>"
                    f"</div>"
                ))
    
    def create_calibration_flow_chart(self):
        """Create a flow chart showing the calibration process steps"""
        with self.graph_output:
            clear_output()
            
            # Create a new graph for the flow chart
            dot = graphviz.Digraph(comment='Calibration Process Flow')
            dot.attr(rankdir='TB')  # Top to bottom layout
            dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
            
            # Add process steps
            dot.node('start', 'Start', shape='oval')
            dot.node('connect', 'Connect to Controller')
            dot.node('create_profiles', 'Create MCU & Motor Profiles')
            dot.node('associate', 'Associate Motor with MCU\nConfigure Step/Dir Pins')
            dot.node('setup', 'Set Up Syringe Pump\nDefine Syringe Parameters')
            dot.node('trial1', 'Run First Calibration Trial\n(Low Frequency)')
            dot.node('measure1', 'Measure Dispensed Volume')
            dot.node('trial2', 'Run Second Calibration Trial\n(High Frequency)')
            dot.node('measure2', 'Measure Dispensed Volume')
            dot.node('calculate', 'Calculate Calibration Parameters')
            dot.node('test', 'Test Calibrated Motor')
            dot.node('end', 'End', shape='oval')
            
            # Add connections
            dot.edge('start', 'connect')
            dot.edge('connect', 'create_profiles')
            dot.edge('create_profiles', 'associate')
            dot.edge('associate', 'setup')
            dot.edge('setup', 'trial1')
            dot.edge('trial1', 'measure1')
            dot.edge('measure1', 'trial2')
            dot.edge('trial2', 'measure2')
            dot.edge('measure2', 'calculate')
            dot.edge('calculate', 'test')
            dot.edge('test', 'end')
            
            # Add a decision point for verification
            dot.node('verify', 'Verify Calibration\nAccuracy?', shape='diamond', fillcolor='lightyellow')
            dot.edge('test', 'verify')
            dot.edge('verify', 'setup', label='No - Recalibrate')
            dot.edge('verify', 'end', label='Yes - Calibration Complete')
            
            # Add title
            dot.attr(label='Syringe Pump Calibration Process Flow')
            dot.attr(fontsize='16')
            
            # Render the flow chart
            try:
                display(dot)
                
                # Add explanatory text
                explanation_html = """
                <div style="margin-top: 20px; padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9;">
                    <h4>Calibration Process Overview:</h4>
                    <ol>
                        <li><strong>Setup:</strong> Connect to the controller, create profiles for MCUs and motors</li>
                        <li><strong>Association:</strong> Associate motors with MCUs and configure step/dir pins</li>
                        <li><strong>Calibration Trials:</strong> Perform two calibration runs at different frequencies</li>
                        <li><strong>Calculation:</strong> Generate calibration parameters based on measured volumes</li>
                        <li><strong>Verification:</strong> Test the calibrated motor to verify accuracy</li>
                    </ol>
                </div>
                """
                display(HTML(explanation_html))
                
            except Exception as e:
                print(f"Error rendering flow chart: {e}")
                print("Make sure you have Graphviz installed.")
    
    def generate_mcu_motor_graph(self, _=None):
        """Generate a GraphViz visualization showing MCU and motor relationships"""
        with self.graph_output:
            clear_output()
            
            mcus = self.controller.get_mcus()
            motors = self.controller.get_motors()
            
            if not mcus:
                print("No MCU profiles found.")
                return
                
            # Create a new graph
            dot = graphviz.Digraph(comment='MCU-Motor Relationships')
            dot.attr(rankdir='LR')  # Left to right layout
            dot.attr('node', shape='box', style='filled')
            
            # Add timestamp to the graph
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dot.attr(label=f'MCU-Motor Relationship Map\nGenerated: {timestamp}')
            dot.attr(fontsize='12')
            
            # Add MCUs (color them blue)
            for mcu in mcus:
                mcu_id = mcu.get('uniqueID')
                mcu_name = mcu.get('name', 'Unknown MCU')
                port_info = ""
                if "lastConnectedPort" in mcu:
                    port_info = f"\nPort: {mcu['lastConnectedPort']}"
                dot.node(f'mcu_{mcu_id}', f"{mcu_name}{port_info}", fillcolor='lightblue')
            
            # Add Motors (using different colors based on calibration status)
            for motor in motors:
                motor_id = motor.get('uniqueID')
                motor_name = motor.get('name', 'Unknown Motor')
                
                # Use different colors for calibrated vs uncalibrated motors
                if motor.get('calibrated'):
                    fillcolor = 'palegreen'
                    # If it has syringe info, add it to the label
                    if "syringeInfo" in motor:
                        si = motor["syringeInfo"]
                        syringe_label = f"\n{si.get('brand')} {si.get('model')}\n{si.get('volumeML')}mL"
                        motor_name += syringe_label
                        
                        # Add flow rate range if available
                        if "minUPS" in motor and "maxUPS" in motor:
                            flow_range = f"\n{motor['minUPS']:.3f} - {motor['maxUPS']:.2f} mL/min"
                            motor_name += flow_range
                else:
                    fillcolor = 'lightgray'
                
                dot.node(f'motor_{motor_id}', f"{motor_name}", fillcolor=fillcolor)
            
            # Add edges from MCU to Motors with pin labels
            for mcu in mcus:
                mcu_id = mcu.get('uniqueID')
                
                for motor_ref in mcu.get('motors', []):
                    motor_id = motor_ref.get('uniqueID')
                    step_pin = motor_ref.get('step', '?')
                    dir_pin = motor_ref.get('dir', '?')
                    
                    # Edge label with pins
                    edge_label = f"Step: {step_pin}\nDir: {dir_pin}"
                    
                    dot.edge(f'mcu_{mcu_id}', f'motor_{motor_id}', label=edge_label)
            
            # Render the graph
            try:
                display(dot)
                
                # Add a legend
                legend_html = """
                <div style="margin-top: 20px; padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9;">
                    <h4>Graph Legend:</h4>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="width: 20px; height: 20px; background-color: lightblue; margin-right: 10px;"></div>
                        <div>MCU Profile</div>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="width: 20px; height: 20px; background-color: palegreen; margin-right: 10px;"></div>
                        <div>Calibrated Motor Profile</div>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 20px; height: 20px; background-color: lightgray; margin-right: 10px;"></div>
                        <div>Uncalibrated Motor Profile</div>
                    </div>
                </div>
                """
                display(HTML(legend_html))
                
            except Exception as e:
                print(f"Error rendering graph: {e}")
                print("Make sure you have Graphviz installed. You can install it via:")
                print("!pip install graphviz")
                print("Note: You might also need to install the Graphviz system package.")
    
    def create_tab_layout(self):
        """Create the visualization tab layout"""
        # Create the calibration plot section
        calibration_plot_section = widgets.VBox([
            widgets.HTML("<h3>Motor Calibration Plot</h3>"),
            widgets.HTML("<p>Visualize the calibration curve for a selected motor profile</p>"),
            widgets.HBox([self.motor_dropdown, self.refresh_motors_button, self.generate_plot_button]),
            self.calibration_plot_output
        ])
        
        # Create the diameter comparison section with more space
        diameter_comparison_section = widgets.VBox([
            self.diameter_comparison_title,
            self.diameter_comparison_description,
            widgets.HBox([self.diameter_motor_dropdown]),
            widgets.HBox([self.new_diameter_input, self.generate_diameter_plot_button]),
            self.diameter_plot_output
        ], layout=widgets.Layout(margin='20px 0'))
        
        # Return a VBox with both sections, adding more vertical spacing
        return widgets.VBox([
            widgets.HTML("<h2>Calibration Data Visualizations</h2>"),
            calibration_plot_section,
            widgets.HTML("<hr style='margin: 30px 0;'>"),  # Increased margin from 20px to 30px
            diameter_comparison_section
        ], layout=widgets.Layout(padding='20px'))  # Added overall padding
    
    def create_overview_tab(self):
        """Create the overview tab with process flow chart and motor-MCU mapping"""
        # Create flow chart button
        self.flow_chart_button = widgets.Button(
            description='Show Process Flow Chart',
            button_style='info',
            icon='project-diagram'
        )
        self.flow_chart_button.on_click(lambda _: self.create_calibration_flow_chart())
        
        # Create the flow chart section
        flow_chart_section = widgets.VBox([
            widgets.HTML("<h3>Calibration Process Flow Chart</h3>"),
            widgets.HTML("<p>Visual guide to the calibration workflow</p>"),
            self.flow_chart_button,
        ])
        
        # Create the MCU-motor mapping section
        mcu_motor_section = widgets.VBox([
            widgets.HTML("<h3>MCU-Motor Relationship Graph</h3>"),
            widgets.HTML("<p>Visualize how motors are connected to MCUs</p>"),
            self.generate_graph_button,
        ])
        
        # Combine both sections with a shared output area
        overview_tab = widgets.VBox([
            widgets.HTML("<h2>Calibration System Overview</h2>"),
            widgets.HTML("<p>This tool helps you calibrate syringe pumps by associating motors with microcontrollers and performing calibration trials.</p>"),
            widgets.HBox([
                flow_chart_section,
                mcu_motor_section
            ]),
            self.graph_output
        ])
        
        return overview_tab
