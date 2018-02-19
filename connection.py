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


def test():
    print('hello!')
    with Valve('/dev/tty.usbserial') as v:
        e = DeviceExecutor()
        for i in range(100):
            e.submit(v, i, v.set_position, (i%9)+1)
        e.submit(v, 4.5, v.set_position, 8)
        print (e._task_queue)
        e.run()
