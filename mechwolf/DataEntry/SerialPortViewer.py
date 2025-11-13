import platform
import subprocess
import glob
import os
from typing import List


class SerialPortViewer:
    """
    SerialPortViewer is a class that provides functionality to list serial ports available on the system.
    Methods:
        __init__():
            Initializes the SerialPortViewer instance.
        run():
            Executes the main functionality of the SerialPortViewer by calling the show_serial_ports method.
        show_serial_ports():
            Detects and lists the serial ports available on the system based on the operating system.
            - On Linux, it lists ports in the /dev/serial/by-id directory.
            - On Windows, it uses PowerShell to get the list of serial ports.
            - On macOS (Darwin), it lists ports matching the /dev/cu.* pattern.
            - For unsupported operating systems, it prints an error message.
    """

    def __init__(self) -> None:
        pass

    def run(self) -> None:
        self.show_serial_ports()

    def show_serial_ports(self) -> None:
        os_type = platform.system()

        if (
            os_type == "Linux"
            and os.path.exists("/proc/device-tree/model")
            and "Raspberry Pi" in open("/proc/device-tree/model").read()
        ):
            print(
                "Plug in your devices one by one and then note down the serial IDs. The order in which you plug in the pumps will be assigned as serial ports /dev/ttyACM0, /dev/ttyACM1, /dev/ttyACM2, and so on."
            )
            if os.path.exists("/dev/serial/by-id"):
                ports: List[str] = os.listdir("/dev/serial/by-id")
                if ports:
                    for port in ports:
                        print(port)
                else:
                    print("No device/serial ports connected.")
            else:
                print("No device/serial ports found.")
        elif os_type == "Linux":
            if os.path.exists("/dev/serial/by-id"):
                ports: List[str] = os.listdir("/dev/serial/by-id")
                if ports:
                    for port in ports:
                        print(port)
                else:
                    print("No device/serial ports connected.")
            else:
                print("No device/serial ports found.")
        elif os_type == "Windows":
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-WMIObject Win32_SerialPort | Select-Object -ExpandProperty DeviceID",
                ],
                capture_output=True,
                text=True,
            )
            output = result.stdout.strip()
            if output:
                print(output)
            else:
                print("No device/serial ports connected.")
        elif os_type == "Darwin":  # macOS
            serial_ports: List[str] = glob.glob("/dev/cu.*")
            if serial_ports:
                print(serial_ports)
            else:
                print("No device/serial ports connected.")
        else:
            print("Unsupported operating system.")
