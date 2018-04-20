from .pump import Pump
from . import ureg
import serial

class VarianPump(Pump):
    '''A Varian pump.
    '''
    def __init__(self, name=None, serial_port=None, max_rate=0):
        super().__init__(name=name)
        self.rate = ureg.parse_expression("0 ml/min")
        self.max_rate = max_rate
        self.serial_port = serial_port

        #VARIAN PUMP SPECIFIC OPTIONS
        self.pump_id = 0

    def __enter__(self):

        self.ser = serial.Serial(self.serial_port)
        self.ser.baudrate = 19200
        self.ser.parity = 'E'
        self.ser.stopbits = 1
        self.ser.timeout = 1
        self.lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()

    def lock(self):
        lock_command = [0xFF,self.pump_id,0x0A,0x4C,0x0D]
        self.ser.write(lock_command)
        print(self.ser.read_all())

    def set_flow(self,flow_rate):
        #Flow rate must be supplied as an string from 000000 to 100000, where 100000 = 100% of the maximum pump flow rate.
        percentage = 1000 * flow_rate / self.max_rate

        flow_command = [0xFF, self.pump_id, 0x0A, 0x58]
        
        flow_command.extend(list(str(int(percentage)).encode()))
        flow_command.append(0x0D)
        self.ser.write(flow_command)
        print(self.ser.read_all())    

    def update(self):
        self.set_flow(self.rate)

    def config(self):
        return dict(serial_port=(str, None), max_rate=(int, None))
