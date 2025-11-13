# *************************************************************************
# FreeStep Controller (Python CLI Version)
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

import json
import os
import time
import random
import string
import threading
from pathlib import Path
import serial
import serial.tools.list_ports

class SerialManager:
    """Manages serial connections to MCUs"""
    def __init__(self):
        self.open_ports = {}  # port_name -> serial_connection
        self.listeners = []
        self.read_threads = {}  # port_name -> thread
        self.stop_flags = {}    # port_name -> stop flag
        
    def list_ports(self):
        """Lists all available serial ports"""
        return [{"path": port.device, "description": port.description} 
                for port in serial.tools.list_ports.comports()]
    
    def is_port_open(self, port_name):
        """Checks if a port is currently open"""
        return port_name in self.open_ports and self.open_ports[port_name].is_open
    
    def open_port(self, port_name, baudrate=9600):
        """Opens a serial port"""
        if port_name in self.open_ports:
            print(f"Port {port_name} is already open")
            return True
            
        try:
            port = serial.Serial(port_name, baudrate, timeout=1)
            self.open_ports[port_name] = port
            
            # Set flag for this port to False (don't stop)
            self.stop_flags[port_name] = False
            
            # Start a thread to read responses
            thread = threading.Thread(target=self._read_responses, args=(port_name,), daemon=True)
            self.read_threads[port_name] = thread
            thread.start()
            
            print(f"Opened port {port_name} at {baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Error opening port {port_name}: {e}")
            return False
    
    def close_port(self, port_name):
        """Closes a serial port"""
        if port_name in self.open_ports:
            try:
                # Signal the reading thread to stop
                self.stop_flags[port_name] = True
                
                # Wait a short time for thread to notice the flag
                time.sleep(0.2)
                
                # Now close the port
                self.open_ports[port_name].close()
                
                # Clean up resources
                del self.open_ports[port_name]
                if port_name in self.read_threads:
                    del self.read_threads[port_name]
                if port_name in self.stop_flags:
                    del self.stop_flags[port_name]
                    
                print(f"Closed port {port_name}")
                return True
            except Exception as e:
                print(f"Error closing port {port_name}: {e}")
                return False
        return False
    
    def close_all_ports(self):
        """Closes all open ports"""
        for port_name in list(self.open_ports.keys()):
            self.close_port(port_name)
    
    def send_command(self, port_name, command_data):
        """Sends a command to a specific port"""
        if port_name not in self.open_ports:
            print(f"Error: Port {port_name} is not open")
            return False
            
        try:
            port = self.open_ports[port_name]
            
            # Handle syringe diameter calibration if provided
            if "syringeDiameter" in command_data and "freq" in command_data:
                diameter = command_data["syringeDiameter"]
                # Calculate cross-sectional area
                radius = diameter / 2.0
                cross_sectional_area = 3.14159 * (radius ** 2)
                
                # Get reference diameter from command data or use default
                reference_diameter = command_data.get("referenceDiameter", 8.0)  # Default 8mm diameter
                reference_radius = reference_diameter / 2.0
                reference_area = 3.14159 * (reference_radius ** 2)
                
                # Scale frequency based on the ratio of cross-sectional areas
                # When area increases, frequency should decrease proportionally to maintain the same flow rate
                area_ratio = reference_area / cross_sectional_area if cross_sectional_area > 0 else 1.0
                command_data["freq"] = command_data["freq"] * area_ratio
                
                print(f"Calibrated for syringe diameter: {diameter}mm (ratio: {area_ratio:.4f})")
                
                # Remove the syringeDiameter field before sending to avoid confusion at the MCU
                del command_data["syringeDiameter"]
                if "referenceDiameter" in command_data:
                    del command_data["referenceDiameter"]
            
            # Convert frequency to integer for stepper motor control
            if "freq" in command_data:
                command_data["freq"] = int(round(command_data["freq"]))
            
            # Make sure step and dir pins are integers
            if "stepPin" in command_data:
                command_data["stepPin"] = int(command_data["stepPin"])
            if "dirPin" in command_data:
                command_data["dirPin"] = int(command_data["dirPin"])
                
            # Use compact JSON formatting with no whitespace
            json_data = json.dumps(command_data, separators=(',', ':'))
            port.write(f"{json_data}\n".encode())
            print(f"Sent command to {port_name}: {json_data}")
            return True
        except Exception as e:
            print(f"Error sending command to {port_name}: {e}")
            return False
    
    # This is a specialized version that formats commands directly like the Arduino expects
    def send_formatted_command(self, port_name, type, step_pin, dir_pin, freq, time_value, time_unit, direction):
        """Send a command directly to the specified port with proper formatting for Arduino"""
        if port_name not in self.open_ports:
            print(f"Error: Port {port_name} is not open")
            return False
        
        # Create the command with minimal JSON structure for Arduino's simple parser
        # Convert frequency to integer for stepper motor control
        command = {
            "type": type,
            "stepPin": int(step_pin),
            "dirPin": int(dir_pin),
            "freq": int(round(freq)),
            "timeValue": float(time_value),
            "timeUnit": time_unit,
            "direction": direction
        }
        
        # Convert to JSON string and send
        try:
            json_str = json.dumps(command, separators=(',', ':'))
            port = self.open_ports[port_name]
            if port.is_open:
                port.write((json_str + "\n").encode())
                print(f"Sent formatted command to {port_name}: {json_str}")
                return True
            else:
                print(f"Port {port_name} is no longer open.")
                return False
        except Exception as e:
            print(f"Error sending formatted command to {port_name}: {e}")
        
        return False
    
    def _read_responses(self, port_name):
        """Background thread to read responses from the port"""
        while port_name in self.open_ports:
            # Check if we've been asked to stop
            if port_name in self.stop_flags and self.stop_flags[port_name]:
                print(f"Stopping read thread for {port_name}")
                break
                
            try:
                # Only try to read if port is still open
                port = self.open_ports.get(port_name)
                if not port or not port.is_open:
                    break
                    
                if port.in_waiting:
                    data = port.readline().decode().strip()
                    print(f"Received from {port_name}: {data}")
                    for callback in self.listeners:
                        callback(port_name, data)
            except Exception as e:
                # Don't print error if we're stopping intentionally
                if not (port_name in self.stop_flags and self.stop_flags[port_name]):
                    print(f"Error reading from {port_name}: {e}")
                break
            time.sleep(0.1)
        
        print(f"Read thread for {port_name} has exited")
    
    def add_response_listener(self, callback):
        """Add a callback function to receive responses"""
        self.listeners.append(callback)
    
    def remove_response_listener(self, callback):
        """Remove a callback function"""
        if callback in self.listeners:
            self.listeners.remove(callback)

class ProfileManager:
    """Manages MCU and motor profiles"""
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.mcu_path = os.path.join(base_dir, "MCUs.json")
        self.motors_path = os.path.join(base_dir, "motors.json")
    
    def load_mcus(self):
        """Loads MCU profiles from JSON file"""
        try:
            if os.path.exists(self.mcu_path):
                with open(self.mcu_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading MCUs: {e}")
            return []
    
    def save_mcus(self, mcus):
        """Saves MCU profiles to JSON file"""
        try:
            with open(self.mcu_path, 'w') as f:
                json.dump(mcus, f, indent=2)
            print(f"Saved MCUs to {self.mcu_path}")
            return True
        except Exception as e:
            print(f"Error saving MCUs: {e}")
            return False
    
    def load_motors(self):
        """Loads motor profiles from JSON file"""
        try:
            if os.path.exists(self.motors_path):
                with open(self.motors_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading motors: {e}")
            return []
    
    def save_motors(self, motors):
        """Saves motor profiles to JSON file"""
        try:
            with open(self.motors_path, 'w') as f:
                json.dump(motors, f, indent=2)
            print(f"Saved motors to {self.motors_path}")
            return True
        except Exception as e:
            print(f"Error saving motors: {e}")
            return False
    
    def import_profiles(self, file_path, profile_type):
        """Imports profiles from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if profile_type == "mcus":
                self.save_mcus(data)
            elif profile_type == "motors":
                self.save_motors(data)
            else:
                print(f"Unknown profile type: {profile_type}")
                return False
            return True
        except Exception as e:
            print(f"Error importing profiles: {e}")
            return False
    
    def export_profiles(self, file_path, profile_type):
        """Exports profiles to a JSON file"""
        try:
            if profile_type == "mcus":
                data = self.load_mcus()
            elif profile_type == "motors":
                data = self.load_motors()
            else:
                print(f"Unknown profile type: {profile_type}")
                return False
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting profiles: {e}")
            return False
    
    def add_mcu(self, name="New MCU"):
        """Adds a new MCU profile"""
        mcus = self.load_mcus()
        unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        mcus.append({
            "uniqueID": unique_id,
            "name": name,
            "motors": []
        })
        self.save_mcus(mcus)
        return unique_id
    
    def update_mcu(self, mcu_data):
        """Updates an MCU profile"""
        mcus = self.load_mcus()
        for i, mcu in enumerate(mcus):
            if mcu["uniqueID"] == mcu_data["uniqueID"]:
                mcus[i] = mcu_data
                self.save_mcus(mcus)
                return True
        # If not found, add as new
        mcus.append(mcu_data)
        self.save_mcus(mcus)
        return True
    
    def delete_mcu(self, unique_id):
        """Deletes an MCU profile"""
        mcus = self.load_mcus()
        mcus = [mcu for mcu in mcus if mcu["uniqueID"] != unique_id]
        self.save_mcus(mcus)
    
    def add_motor(self, name="New Motor"):
        """Adds a new motor profile"""
        motors = self.load_motors()
        unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        motors.append({
            "uniqueID": unique_id,
            "name": name,
            "calibrated": False
        })
        self.save_motors(motors)
        return unique_id
    
    def update_motor(self, motor_data):
        """Updates a motor profile"""
        motors = self.load_motors()
        for i, motor in enumerate(motors):
            if motor["uniqueID"] == motor_data["uniqueID"]:
                motors[i] = motor_data
                self.save_motors(motors)
                return True
        # If not found, add as new
        motors.append(motor_data)
        self.save_motors(motors)
        return True
    
    def delete_motor(self, unique_id):
        """Deletes a motor profile"""
        motors = self.load_motors()
        motors = [motor for motor in motors if motor["uniqueID"] != unique_id]
        self.save_motors(motors)

class CommandProcessor:
    """Processes commands for stepper motors"""
    def __init__(self, serial_manager, profile_manager):
        self.serial_manager = serial_manager
        self.profile_manager = profile_manager
    
    def process_command(self, command_data):
        """Processes a command and sends it to the appropriate MCU"""
        cmd_type = command_data.get("type")
        com_port = command_data.get("comPort")
        
        if cmd_type == "COMOpen":
            return self.serial_manager.open_port(com_port)
        elif cmd_type == "COMClose":
            return self.serial_manager.close_port(com_port)
        elif cmd_type in ["basic", "timed", "stop"]:
            return self.serial_manager.send_command(com_port, command_data)
        else:
            print(f"Unknown command type: {cmd_type}")
            return False
    
    def run_basic(self, com_port, direction, freq, step_pin, dir_pin):
        """Runs a motor in basic mode"""
        command = {
            "type": "basic",
            "direction": direction,
            "freq": freq,
            "stepPin": step_pin,
            "dirPin": dir_pin
        }
        return self.serial_manager.send_command(com_port, command)
    
    def run_timed(self, com_port, direction, freq, step_pin, dir_pin, time_value, time_unit):
        """Runs a motor in timed mode"""
        command = {
            "type": "timed",
            "direction": direction,
            "freq": freq,
            "stepPin": step_pin,
            "dirPin": dir_pin,
            "timeValue": time_value,
            "timeUnit": time_unit
        }
        return self.serial_manager.send_command(com_port, command)
    
    def stop_motor(self, com_port, step_pin, dir_pin):
        """Stops a motor"""
        command = {
            "type": "stop",
            "stepPin": step_pin,
            "dirPin": dir_pin
        }
        return self.serial_manager.send_command(com_port, command)
    
    def convert_ups_to_freq(self, motor_profile, ups):
        """Converts flow rate (mL/min) to frequency using calibration data"""
        if not motor_profile.get("calibrated"):
            print("Error: Motor is not calibrated")
            return None
            
        # Get the calibration values
        max_ups = motor_profile.get("maxUPS")
        min_ups = motor_profile.get("minUPS")
        intercept = motor_profile.get("UPSIntercept")
        slope = motor_profile.get("UPSSlope")
        
        # Check if flow rate is within calibration
        if ups >= max_ups:
            print(f"Error: flow rate exceeds calibration (max: {max_ups:.2f} mL/min)")
            return None
        elif ups <= min_ups:
            print(f"Error: flow rate is below calibration (min: {min_ups:.6f} mL/min)")
            return None
            
        # Convert flow rate to frequency
        freq = (ups - intercept) / slope
        return freq

class FreeStepController:
    """Main controller class"""
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.serial_manager = SerialManager()
        self.command_processor = CommandProcessor(self.serial_manager, self.profile_manager)
        
        # Register a response listener
        self.serial_manager.add_response_listener(self.handle_response)
        
    def handle_response(self, port, data):
        """Handle response from the MCU"""
        pass  # Additional processing can be added here
    
    def list_ports(self):
        """List available serial ports"""
        ports = self.serial_manager.list_ports()
        print("\nAvailable ports:")
        for i, port in enumerate(ports):
            print(f"{i+1}. {port['path']} - {port['description']}")
        return ports
    
    def connect_port(self, port):
        """Connect to a serial port"""
        return self.serial_manager.open_port(port)
    
    def disconnect_port(self, port):
        """Disconnect from a serial port"""
        return self.serial_manager.close_port(port)
    
    def get_mcus(self):
        """Get MCU profiles"""
        return self.profile_manager.load_mcus()
    
    def get_motors(self):
        """Get motor profiles"""
        return self.profile_manager.load_motors()
    
    def add_mcu(self, name="New MCU"):
        """Add a new MCU profile"""
        return self.profile_manager.add_mcu(name)
    
    def add_motor(self, name="New Motor"):
        """Add a new motor profile"""
        return self.profile_manager.add_motor(name)
    
    def run_basic_command(self, port, motor_profile, mcu_profile, ups, direction, diameter_ratio=1.0):
        """Run a motor in basic mode using profiles"""
        if not motor_profile.get("calibrated", False):
            print("Error: Motor is not calibrated")
            return False
            
        # Find the motor in the MCU profile
        motor_config = None
        for motor in mcu_profile.get("motors", []):
            if motor.get("uniqueID") == motor_profile.get("uniqueID"):
                motor_config = motor
                break
                
        if not motor_config:
            print("Error: Motor not found in MCU profile")
            return False
            
        # Get step and dir pins
        step_pin = motor_config.get("step")
        dir_pin = motor_config.get("dir")
        
        # Convert UPS to frequency
        freq = self.command_processor.convert_ups_to_freq(motor_profile, ups)
        if freq is None:
            return False
            
        # Apply diameter ratio to adjust frequency
        if diameter_ratio != 1.0:
            freq = freq * diameter_ratio
            print(f"Adjusted frequency: {freq:.2f}Hz (after diameter ratio applied)")
        
        # Send the command
        return self.command_processor.run_basic(port, direction, freq, step_pin, dir_pin)
    
    def run_timed_command(self, port, motor_profile, mcu_profile, ups, time_value, time_unit, direction):
        """Run a motor for a specific time using profiles"""
        if not motor_profile.get("calibrated", False):
            print("Error: Motor is not calibrated")
            return False
            
        # Find the motor in the MCU profile
        motor_config = None
        for motor in mcu_profile.get("motors", []):
            if motor.get("uniqueID") == motor_profile.get("uniqueID"):
                motor_config = motor
                break
                
        if not motor_config:
            print("Error: Motor not found in MCU profile")
            return False
            
        # Get step and dir pins
        step_pin = motor_config.get("step")
        dir_pin = motor_config.get("dir")
        
        # Convert UPS to frequency
        freq = self.command_processor.convert_ups_to_freq(motor_profile, ups)
        if freq is None:
            return False
            
        # Create the command
        command = {
            "type": "timed",
            "direction": direction,
            "freq": freq,
            "stepPin": step_pin,
            "dirPin": dir_pin,
            "timeValue": time_value,
            "timeUnit": time_unit
        }
        
        # Add syringe diameter info if available
        if "syringeInfo" in motor_profile:
            if "innerDiameterMM" in motor_profile["syringeInfo"]:
                command["syringeDiameter"] = motor_profile["syringeInfo"]["innerDiameterMM"]
                print(f"Using syringe inner diameter: {motor_profile['syringeInfo']['innerDiameterMM']}mm")
            elif "diameterMM" in motor_profile["syringeInfo"]:
                command["syringeDiameter"] = motor_profile["syringeInfo"]["diameterMM"]
                print(f"Using syringe diameter: {motor_profile['syringeInfo']['diameterMM']}mm")
        
        # Send the command
        return self.serial_manager.send_command(port, command)
    
    def stop_command(self, port, mcu_profile, motor_profile):
        """Stop a motor using profiles"""
        # Find the motor in the MCU profile
        motor_config = None
        for motor in mcu_profile.get("motors", []):
            if motor.get("uniqueID") == motor_profile.get("uniqueID"):
                motor_config = motor
                break
                
        if not motor_config:
            print("Error: Motor not found in MCU profile")
            return False
            
        # Get step and dir pins
        step_pin = motor_config.get("step")
        dir_pin = motor_config.get("dir")
        
        # Send the stop command
        return self.command_processor.stop_motor(port, step_pin, dir_pin)
    
    def emergency_stop(self):
        """Stop all motors on all connected MCUs"""
        mcus = self.profile_manager.load_mcus()
        
        for port_name in self.serial_manager.open_ports:
            for mcu in mcus:
                for motor in mcu.get("motors", []):
                    step_pin = motor.get("step")
                    dir_pin = motor.get("dir")
                    self.command_processor.stop_motor(port_name, step_pin, dir_pin)
        
        print("Emergency stop sent to all motors")
        return True
    
    def cleanup(self):
        """Clean up resources before exiting"""
        self.serial_manager.close_all_ports()

# Example usage as a CLI tool
if __name__ == "__main__":
    controller = FreeStepController()
    
    try:
        print("FreeStep Controller CLI")
        print("Type 'help' for a list of commands")
        
        while True:
            cmd = input("> ").strip().lower()
            
            if cmd == "help":
                print("\nCommands:")
                print("  ports - List available serial ports")
                print("  connect <port> - Connect to a port")
                print("  disconnect <port> - Disconnect from a port")
                print("  mcus - List MCU profiles")
                print("  motors - List motor profiles")
                print("  add_mcu <name> - Add a new MCU profile")
                print("  add_motor <name> - Add a new motor profile")
                print("  run <port> <mcu_id> <motor_id> <ups> <direction> - Run a motor")
                print("  run_timed <port> <mcu_id> <motor_id> <ups> <time> <unit> <direction> - Run a motor for a time")
                print("  stop <port> <mcu_id> <motor_id> - Stop a motor")
                print("  stop_all - Emergency stop all motors")
                print("  exit - Exit the program")
            
            elif cmd == "ports":
                controller.list_ports()
            
            elif cmd.startswith("connect "):
                port = cmd.split(" ", 1)[1]
                if controller.connect_port(port):
                    print(f"Connected to {port}")
                else:
                    print(f"Failed to connect to {port}")
            
            elif cmd.startswith("disconnect "):
                port = cmd.split(" ", 1)[1]
                if controller.disconnect_port(port):
                    print(f"Disconnected from {port}")
                else:
                    print(f"Failed to disconnect from {port}")
            
            elif cmd == "mcus":
                mcus = controller.get_mcus()
                print("\nMCU Profiles:")
                for mcu in mcus:
                    print(f"  ID: {mcu.get('uniqueID')}, Name: {mcu.get('name')}")
            
            elif cmd == "motors":
                motors = controller.get_motors()
                print("\nMotor Profiles:")
                for motor in motors:
                    calibrated = "Yes" if motor.get("calibrated") else "No"
                    print(f"  ID: {motor.get('uniqueID')}, Name: {motor.get('name')}, Calibrated: {calibrated}")
            
            elif cmd.startswith("add_mcu "):
                name = cmd.split(" ", 1)[1]
                id = controller.add_mcu(name)
                print(f"Added MCU profile '{name}' with ID {id}")
            
            elif cmd.startswith("add_motor "):
                name = cmd.split(" ", 1)[1]
                id = controller.add_motor(name)
                print(f"Added motor profile '{name}' with ID {id}")
            
            elif cmd.startswith("run "):
                parts = cmd.split(" ")
                if len(parts) != 6:
                    print("Usage: run <port> <mcu_id> <motor_id> <ups> <direction>")
                else:
                    port = parts[1]
                    mcu_id = parts[2]
                    motor_id = parts[3]
                    ups = float(parts[4])
                    direction = parts[5]
                    
                    # Find the profiles
                    mcus = controller.get_mcus()
                    motors = controller.get_motors()
                    
                    mcu_profile = next((mcu for mcu in mcus if mcu.get("uniqueID") == mcu_id), None)
                    motor_profile = next((motor for motor in motors if motor.get("uniqueID") == motor_id), None)
                    
                    if mcu_profile and motor_profile:
                        controller.run_basic_command(port, motor_profile, mcu_profile, ups, direction)
                    else:
                        print("Error: MCU or motor profile not found")
            
            elif cmd.startswith("run_timed "):
                parts = cmd.split(" ")
                if len(parts) != 8:
                    print("Usage: run_timed <port> <mcu_id> <motor_id> <ups> <time> <unit> <direction>")
                else:
                    port = parts[1]
                    mcu_id = parts[2]
                    motor_id = parts[3]
                    ups = float(parts[4])
                    time_value = float(parts[5])
                    time_unit = parts[6]
                    direction = parts[7]
                    
                    # Find the profiles
                    mcus = controller.get_mcus()
                    motors = controller.get_motors()
                    
                    mcu_profile = next((mcu for mcu in mcus if mcu.get("uniqueID") == mcu_id), None)
                    motor_profile = next((motor for motor in motors if motor.get("uniqueID") == motor_id), None)
                    
                    if mcu_profile and motor_profile:
                        controller.run_timed_command(port, motor_profile, mcu_profile, ups, time_value, time_unit, direction)
                    else:
                        print("Error: MCU or motor profile not found")
            
            elif cmd.startswith("stop "):
                parts = cmd.split(" ")
                if len(parts) != 4:
                    print("Usage: stop <port> <mcu_id> <motor_id>")
                else:
                    port = parts[1]
                    mcu_id = parts[2]
                    motor_id = parts[3]
                    
                    # Find the profiles
                    mcus = controller.get_mcus()
                    motors = controller.get_motors()
                    
                    mcu_profile = next((mcu for mcu in mcus if mcu.get("uniqueID") == mcu_id), None)
                    motor_profile = next((motor for motor in motors if motor.get("uniqueID") == motor_id), None)
                    
                    if mcu_profile and motor_profile:
                        controller.stop_command(port, mcu_profile, motor_profile)
                    else:
                        print("Error: MCU or motor profile not found")
            
            elif cmd == "stop_all":
                controller.emergency_stop()
            
            elif cmd == "exit":
                break
            
            else:
                print("Unknown command. Type 'help' for a list of commands.")
    
    finally:
        controller.cleanup()
        print("Exiting FreeStep Controller CLI")
