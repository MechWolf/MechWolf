import mechwolf as mw
import time
from mechwolf.components.contrib.freestep_3DSyringePump_controller import FreeStepController

# Shared controller instance and port tracking for all FreeStepPump instances
_shared_controllers = {}  # port -> controller
_port_users = {}  # port -> list of pump instances

class FreeStepPump(mw.Pump):
    """
    A MechWolf component for controlling FreeStep 3D syringe pumps.

    Arguments:
    - `serial_port`: Serial port through which the device is connected (e.g., "COM3" or "/dev/ttyUSB0").
    - `mcu_id`: The unique ID of the MCU profile.
    - `motor_id`: The unique ID of the motor profile.
    - `syringe_volume`: The volume of the syringe (in mL).
    - `syringe_diameter`: The diameter of the syringe (in mm).
    - `name` (optional): The name of the syringe pump instance. Defaults to `None`.
    """

    metadata = {
        "author": [
            {
                "first_name": "Prashant",
                "last_name": "Kumar",
                "email": "pprashan@iu.edu",
                "institution": "Indiana University Bloomington, Departemnt of Chemistry",
                "github_username": "Prashant-Kumar-IU",
            }
        ],
        "stability": "beta",
        "supported": True,
    }

    def __init__(self, serial_port, mcu_id, motor_id, syringe_volume, syringe_diameter, name=None):
        super().__init__(name=name)
        self.serial_port = serial_port
        self.mcu_id = mcu_id
        self.motor_id = motor_id
        self.syringe_volume = mw._ureg.parse_expression(syringe_volume)
        self.syringe_diameter = mw._ureg.parse_expression(syringe_diameter)
        self._mcu_profile = None
        self._motor_profile = None
        self._port_initialized = False
        self._last_rate = 0
        
    def __enter__(self):
        global _shared_controllers, _port_users
        
        print(f"Initializing {self.name} on {self.serial_port}...")
        
        # Add this pump to port users
        if self.serial_port not in _port_users:
            _port_users[self.serial_port] = []
        _port_users[self.serial_port].append(self)
        
        # Check if we already have a controller for this port
        if self.serial_port in _shared_controllers:
            print(f"Using existing connection to {self.serial_port} for {self.name}")
            self._controller = _shared_controllers[self.serial_port]
        else:
            # Create a new controller and connect to the port
            print(f"Creating new connection to {self.serial_port} for {self.name}")
            self._controller = FreeStepController()
            if not self._controller.connect_port(self.serial_port):
                raise RuntimeError(f"Failed to connect to {self.serial_port}")
            _shared_controllers[self.serial_port] = self._controller
        
        # Get MCU and motor profiles
        mcus = self._controller.get_mcus()
        motors = self._controller.get_motors()
        
        # Find the specified MCU and motor profiles
        self._mcu_profile = next((mcu for mcu in mcus if mcu.get("uniqueID") == self.mcu_id), None)
        self._motor_profile = next((motor for motor in motors if motor.get("uniqueID") == self.motor_id), None)
        
        if not self._mcu_profile:
            raise RuntimeError(f"MCU with ID {self.mcu_id} not found")
            
        if not self._motor_profile:
            raise RuntimeError(f"Motor with ID {self.motor_id} not found")
            
        if not self._motor_profile.get("calibrated", False):
            raise RuntimeError(f"Motor with ID {self.motor_id} is not calibrated")
            
        # Update syringe info if needed
        if "syringeInfo" not in self._motor_profile:
            self._motor_profile["syringeInfo"] = {
                "brand": "User Defined",
                "model": "User Defined",
                "volumeML": self.syringe_volume.to(mw._ureg.ml).magnitude,
                "innerDiameterMM": self.syringe_diameter.to(mw._ureg.mm).magnitude,
                "calibrationDate": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self._controller.profile_manager.update_motor(self._motor_profile)
        
        # Stop the pump initially to make sure it's in a known state
        self._controller.stop_command(self.serial_port, self._mcu_profile, self._motor_profile)
        self._port_initialized = True
        
        print(f"FreeStepPump {self.name} initialized on {self.serial_port}")
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        global _shared_controllers, _port_users
        
        try:
            # Stop the pump before closing
            if self._port_initialized and self._mcu_profile and self._motor_profile:
                self._controller.stop_command(self.serial_port, self._mcu_profile, self._motor_profile)
                print(f"FreeStepPump {self.name} stopped")
            
            # Remove this pump from port users
            if self.serial_port in _port_users:
                if self in _port_users[self.serial_port]:
                    _port_users[self.serial_port].remove(self)
                
                # Only close port if this was the last pump using it
                if not _port_users[self.serial_port] and self.serial_port in _shared_controllers:
                    print(f"Closing port {self.serial_port} - last pump disconnected")
                    controller = _shared_controllers[self.serial_port]
                    controller.disconnect_port(self.serial_port)
                    controller.cleanup()
                    del _shared_controllers[self.serial_port]
                else:
                    print(f"Keeping port {self.serial_port} open for other pumps")
        except Exception as e:
            print(f"Error during cleanup for {self.name}: {e}")

    async def _update(self):
        """Update pump flow rate - called by MechWolf"""
        if not self._port_initialized or not self._mcu_profile or not self._motor_profile:
            raise RuntimeError(f"Pump {self.name} not properly initialized")
            
        # Convert flow rate to mL/min
        rate_mlmin = self.rate.to(mw._ureg.ml / mw._ureg.min).magnitude
        
        # Only send commands if the rate has changed
        if rate_mlmin != self._last_rate:
            print(f"Rate change detected for {self.name}: {self._last_rate} -> {rate_mlmin} mL/min")
            self._last_rate = rate_mlmin
            
            # Determine operation direction - negative rate means backward/aspiration
            direction = "backward" if rate_mlmin < 0 else "forward"
            # Use absolute value for calculations
            abs_rate = abs(rate_mlmin)
            
            if abs_rate <= 0.000001:  # Near-zero rate threshold for stopping
                # Stop the pump
                print(f"Stopping pump {self.name}")
                self._controller.stop_command(self.serial_port, self._mcu_profile, self._motor_profile)
                print(f"Pump {self.name} stopped")
            else:
                # Run at the specified rate and direction
                print(f"Setting pump {self.name} to {abs_rate} mL/min ({direction})")
                
                # Force pump to run by stopping first
                self._controller.stop_command(self.serial_port, self._mcu_profile, self._motor_profile)
                time.sleep(0.5)  # Small delay to ensure stop takes effect
                
                # Get the calibrated diameter from motor profile
                calibrated_diameter = None
                current_diameter = self.syringe_diameter.to(mw._ureg.mm).magnitude
                
                if "syringeInfo" in self._motor_profile:
                    si = self._motor_profile["syringeInfo"]
                    if "innerDiameterMM" in si:
                        calibrated_diameter = si.get("innerDiameterMM")
                    elif "diameterMM" in si:
                        calibrated_diameter = si.get("diameterMM")
                
                # Calculate area ratio and adjust flow rate if needed
                diameter_ratio = 1.0
                if calibrated_diameter and current_diameter and calibrated_diameter != current_diameter:
                    # The flow rate is proportional to the cross-sectional area
                    # So we need to adjust by the square of the diameter ratio
                    diameter_ratio = (calibrated_diameter / current_diameter) ** 2
                    print(f"Adjusting for different syringe diameter: {current_diameter}mm vs calibrated {calibrated_diameter}mm")
                    print(f"Diameter ratio²: {diameter_ratio:.4f}")
                
                # Now run with the new rate and direction, with automatic diameter adjustment
                success = self._controller.run_basic_command(
                    self.serial_port, 
                    self._motor_profile, 
                    self._mcu_profile,
                    abs_rate,  # Always use positive flow rate value
                    direction,  # Direction determined by sign of original rate
                    diameter_ratio=diameter_ratio  # Pass diameter ratio to adjust frequency
                )
                
                if success:
                    print(f"Pump {self.name} now running at {abs_rate} mL/min ({direction})")
                else:
                    print(f"Failed to set flow rate for {self.name}")
