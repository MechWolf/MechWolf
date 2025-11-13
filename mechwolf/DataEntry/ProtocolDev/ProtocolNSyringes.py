from datetime import timedelta

"""
This module defines the `ProtocolAlgorithm` class, which is responsible for managing and validating
protocols involving pumps and vessels in a laboratory automation setup.
Classes:
    ProtocolAlgorithm: Manages protocol creation and validation for pumps and vessels.
Methods:
    __init__(self, protocol: Protocol, pumps_or_pump: Union[List[ActiveComponent], ActiveComponent, Tuple[ActiveComponent, ...]], 
             *additional_components: ActiveComponent, data_file: str) -> None:
        Initializes the ProtocolAlgorithm with the given protocol, components, and data file.
    _get_pump_vessel_mapping(self) -> List[Dict[str, Any]]:
        Retrieves the predefined pump-vessel mapping from the apparatus.
    validate_inputs(self, configs: List[PumpConfig]) -> bool:
        Validates all inputs from the GUI.
    validate_flow_rate(self, flow_rate: str) -> bool:
        Validates the flow rate format.
    validate_volume(self, volume: str) -> bool:
        Validates the volume format.
    validate_time(self, time: str) -> bool:
        Validates the time format.
    validate_pump_volumes(self, configs: List[PumpConfig]) -> bool:
        Validates that all solutions on the same pump have the same volume.
    create_protocol(self) -> Protocol:
        Creates and returns a protocol based on the validated inputs and pump configurations.
"""
from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from .ProtocolGUICreator import ProtocolGUI, PumpConfig
import re
from typing import List, Dict, Any, Union, Tuple, Optional


class ProtocolAlgorithm:
    def __init__(
        self, protocol: Protocol, pumps_or_pump: Union[List[ActiveComponent], ActiveComponent, Tuple[ActiveComponent, ...]], 
        *additional_components: ActiveComponent, data_file: Optional[str] = None
    ) -> None:
        self.protocol = protocol
        
        # Handle the case where pumps is a list or an individual pump
        if isinstance(pumps_or_pump, list) or isinstance(pumps_or_pump, tuple):
            self.components = list(pumps_or_pump) + list(additional_components)
        else:
            self.components = [pumps_or_pump] + list(additional_components)
            
        self.apparatus = protocol.apparatus

        if data_file is None:
            raise ValueError(
                "data_file parameter is required. Please provide the JSON file path.\n"
                "Example usage:\n"
                "algorithm = ProtocolAlgorithm(P, pumps, data_file='your_config.json')\n"
                "or\n"
                "algorithm = ProtocolAlgorithm(P, pump_1, pump_2, pump_3, data_file='your_config.json')"
            )

        self.data_file = data_file
        # Get the existing pump-vessel mapping from apparatus
        self.pump_vessel_mapping = self._get_pump_vessel_mapping()

    def _get_pump_vessel_mapping(self) -> List[Dict[str, Any]]:
        """Get the predefined pump-vessel mapping from apparatus"""
        mapping = []
        for pump in self.components:
            for connection in self.apparatus.network:
                if connection.from_component == pump:
                    mapping.append(
                        {
                            "pump": pump,
                            "vessel": connection.to_component,
                            "pump_index": self.components.index(pump),
                        }
                    )
                    break
        return mapping

    def validate_inputs(self, configs: List[PumpConfig]) -> bool:
        """Validate all inputs from GUI"""
        for config in configs:
            if (
                not self.validate_flow_rate(str(config.flow_rate))
                or config.flow_rate == 0  # Only check for zero, allow negative values
            ):
                raise ValueError(
                    f"Invalid flow rate: {config.flow_rate}. Please enter a non-zero number followed by 'mL/min'."
                )
            if not self.validate_volume(str(config.volume)) or config.volume <= 0:
                raise ValueError(
                    f"Invalid volume: {config.volume}. Please enter a positive number followed by 'mL'."
                )
            if not self.validate_time(str(config.delay)) or config.delay < 0:
                raise ValueError(
                    f"Invalid delay time: {config.delay}. Please enter a non-negative number followed by 'seconds'."
                )
        return True

    def validate_flow_rate(self, flow_rate: str) -> bool:
        return bool(
            re.match(
                r"^-?\d+(\.\d+)?(?:\s*(?:mL/min|ML/Min|ml/min|ML/min|ML/MIN))?$",
                flow_rate,
            )
        )

    def validate_volume(self, volume: str) -> bool:
        return bool(re.match(r"^\d+(\.\d+)?(?:\s*(?:mL|ML|ml|Ml))?$", volume))

    def validate_time(self, time: str) -> bool:
        return bool(
            re.match(
                r"^\d+(\.\d+)?(?:\s*(?:seconds|sec|s|S|SEC|SECONDS|SEc|Sec))?$", time
            )
        )

    def validate_pump_volumes(self, configs: List[PumpConfig]) -> bool:
        """Validate that all solutions on the same pump have the same volume"""
        # Group configs by pump
        pump_volumes: Dict[ActiveComponent, List[float]] = {}
        for config in configs:
            if config.pump not in pump_volumes:
                pump_volumes[config.pump] = []
            pump_volumes[config.pump].append(config.volume)

        # Check volumes for each pump
        for pump, volumes in pump_volumes.items():
            if len(volumes) > 1 and len(set(volumes)) > 1:
                raise ValueError(
                    f"Pump {pump} has solutions with different volumes: {volumes}. "
                    "All solutions on the same pump must have the same volume."
                )
        return True

    def create_protocol(self) -> Protocol:
        try:
            # Create GUI instance with pump vessels information and data file
            gui = ProtocolGUI(self.pump_vessel_mapping, self.data_file)

            # Wait for GUI completion
            import time
            from IPython import get_ipython
            import asyncio

            while not gui.setup_complete:
                time.sleep(0.1)
                if get_ipython():
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(get_ipython().kernel.do_one_iteration())

            # Validate inputs and pump volumes
            if self.validate_inputs(gui.configs) and self.validate_pump_volumes(
                gui.configs
            ):
                latest_end_time = timedelta(seconds=0)

                # Process each pump configuration
                for config in gui.configs:
                    # Calculate active time based on volume and ABSOLUTE flow rate
                    active_time = timedelta(
                        seconds=(config.volume / abs(config.flow_rate) * 60)
                    )

                    # Calculate total time for this pump (delay + active_time)
                    pump_total_time = timedelta(seconds=config.delay) + active_time

                    # Update latest_end_time if this pump takes longer
                    latest_end_time = max(latest_end_time, pump_total_time)

                    # Add pump operation to protocol with original delay
                    self.protocol.add(
                        config.pump,
                        start=timedelta(seconds=config.delay),
                        duration=active_time,
                        rate=f"{config.flow_rate} mL/min",  # Keep original direction
                    )

                print(f"TOTAL TIME: {latest_end_time}")
                return self.protocol

        except ValueError as e:
            print(f"Validation Error: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None
