# connection.py 
# Manages connection to AWS IoT

import uuid
from concurrent.futures import _base
from collections import deque
import json
import asyncio

class _DeviceWorkItem(object):
    def __init__(self, *, future, device, task_id, time, func, args, kwargs):
        self.future = future
        self.device = device
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.time = time

    async def run(self):
        # TODO: Add in a "with self._condition lock
        await asyncio.sleep(self.time)
        result = self.func(*self.args)
        self.future.set_result(result)
        print("Finished:",self.future.done(),"Result:",self.future.result())
    #TODO Fill in the rest here

class DeviceExecutor(_base.Executor):
    def __init__(self):
        self._task_queue = deque()

    def submit(self, device, time, func, *args, **kwargs):
        task_id = uuid.uuid1().hex
        f = _base.Future()
        task = _DeviceWorkItem(future = f, device=device, task_id=task_id, time=time, func=func, args=args, kwargs=kwargs)
        self._task_queue.append(task)
        return f
        
    def run(self):
        loop = asyncio.get_event_loop()
        coros = []
        for task in self._task_queue:
            coros.append(task.run())
        loop.run_until_complete(asyncio.wait(coros))


import serial

class Valve():
    'Controls a VICI Valco Valve'

    def __init__(self, serial_port, positions = 10):
        self.serial_port = serial_port
        self.positions = positions

    def __enter__(self):
        self.ser = serial.Serial(self.serial_port, 115200, parity = serial.PARITY_NONE, stopbits=1, timeout = 0.1)
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()
        return self
        
    def start(self):
        self.ser = serial.Serial(self.serial_port, 115200, parity = serial.PARITY_NONE, stopbits=1, timeout = 0.1)

    def stop(self):
        self.ser.close()

    def get_position(self):
        self.ser.write(b'CP\r')
        response = self.ser.readline()
        if response:
            position = int(response[2:4]) # Response is in the form 'CPXX\r'
            return position
        else:
            return False

    def set_position(self, position):
        if not position > 0 and position <= self.positions:
            return False
        else:
            message = f'GO{position}\r'
            self.ser.write(message.encode())
            return True

def test():
    print('hello!')
    with Valve('/dev/tty.usbserial') as v:
        e = DeviceExecutor()
        for i in range(100):
            e.submit(v, i, v.set_position, (i%9)+1)
        e.submit(v, 4.5, v.set_position, 8)
        print (e._task_queue)
        e.run()
