from datetime import timedelta

"""
This module defines a class `ProtocolAlgorithm` that creates a protocol for controlling syringe pumps.
Classes:
    ProtocolAlgorithm: A class to create and manage a protocol for syringe pumps.
Methods:
    __init__(self, protocol: Protocol, *components: ActiveComponent) -> None:
        Initializes the ProtocolAlgorithm with a given protocol and components.
    create_protocol(self) -> Protocol:
        Creates a protocol based on user input for flow rate, solvent volume, rinse volume, and switch time.
        Returns:
            Protocol: The created protocol with the specified parameters.
"""
from mechwolf.core.protocol import Protocol
from mechwolf.components import ActiveComponent
from mechwolf.components.contrib.harvardpump import HarvardSyringePump
import re


class ProtocolAlgorithm:
    def __init__(self, protocol: Protocol, *components: ActiveComponent) -> None:
        self.protocol = protocol
        self.components = components

    def create_protocol(self) -> Protocol:
        def parse_flow_rate(flow_rate: str) -> float:
            match = re.match(
                r"(-?\d+(\.\d+)?)\s*(mL/min|ML/Min|ml/min|ML/min|ML/MIN)?", flow_rate
            )
            if match:
                return float(match.group(1))
            else:
                raise ValueError(
                    "Invalid flow rate format. Please enter a number followed by 'mL/min'."
                )

        def parse_volume(volume: str) -> float:
            match = re.match(r"(\d+(\.\d+)?)\s*(mL|ML|ml|Ml)?", volume)
            if match:
                return float(match.group(1))
            else:
                raise ValueError(
                    "Invalid volume format. Please enter a number followed by 'mL'."
                )

        def parse_time(time: str) -> float:
            match = re.match(
                r"(\d+(\.\d+)?)\s*(seconds|sec|s|S|SEC|SECONDS|SEc|Sec)?", time
            )
            if match:
                return float(match.group(1))
            else:
                raise ValueError(
                    "Invalid time format. Please enter a number followed by 'seconds'."
                )

        print("Enter your desired FINAL FLOW RATE (in mL/min):")
        F = input()
        flow_rate = parse_flow_rate(F)

        print("Enter your solvent volume (in mL):")
        V = input()
        solvent_volume = parse_volume(V)

        print("Enter the amount of rinse solvent (in mL):")
        V_Rinse = input()
        rinse_volume = parse_volume(V_Rinse)

        print(
            "Enter how much time you want to stall the pumps so that you can switch syringes (in seconds):"
        )
        t_switch = input()
        switch_time = parse_time(t_switch)

        switch = timedelta(seconds=switch_time)
        current = timedelta(seconds=0)

        # Two syringes are being used so dividing by 2:
        pump_rate = flow_rate / 2

        rinse_time = timedelta(seconds=(rinse_volume / pump_rate * 60))
        active_time = timedelta(seconds=(solvent_volume / pump_rate * 60))

        print("active_time =", active_time)
        print("rinse_time =", rinse_time)

        if isinstance(self.components[0], HarvardSyringePump):
            # Dual-channel pump
            self.protocol.add(
                self.components[0],
                start=current,
                duration=active_time,
                rate=f"{pump_rate} mL/min",
            )
        else:
            # Single-channel pumps
            self.protocol.add(
                self.components[0],
                start=current,
                duration=active_time,
                rate=f"{pump_rate} mL/min",
            )
            self.protocol.add(
                self.components[1],
                start=current,
                duration=active_time,
                rate=f"{pump_rate} mL/min",
            )

        current += active_time + switch

        if isinstance(self.components[0], HarvardSyringePump):
            # Dual-channel pump
            self.protocol.add(
                self.components[0],
                start=current,
                duration=rinse_time,
                rate=f"{pump_rate} mL/min",
            )
        else:
            # Single-channel pumps
            self.protocol.add(
                self.components[0],
                start=current,
                duration=rinse_time,
                rate=f"{pump_rate} mL/min",
            )
            self.protocol.add(
                self.components[1],
                start=current,
                duration=rinse_time,
                rate=f"{pump_rate} mL/min",
            )

        current += active_time + switch

        print(f"TOTAL TIME: {current}")
        return self.protocol
