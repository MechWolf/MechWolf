# connection.py 
# Manages connection to AWS IoT

import uuid
from concurrent.futures import _base
from collections import deque
import json
import asyncio
import Pyro4

class _DeviceWorkItem(object):
    def __init__(self, future, component, time, params):
        self.future = future
        self.component = component
        self.time = time
        self.params = params

    async def run(self):
        # TODO: Add in a "with self._condition lock
        await asyncio.sleep(self.time)
        self.component.update_from_params(self.params)
        result = self.component.update()
        self.future.set_result(result)
        print(f"Finished:\t{self.future.done()}\nResult:\t{self.future.result()}\n".expandtabs(10))
    #TODO Fill in the rest here

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")  
class DeviceExecutor(_base.Executor):
    def __init__(self, component):
        self._task_queue = deque()
        self.component = component

    def submit(self, time, params):
        f = _base.Future()
        task = _DeviceWorkItem(future=f, component=self.component, time=time, params=params)
        self._task_queue.append(task)
        return f
        
    def run(self):
        loop = asyncio.get_event_loop()
        coros = []
        for task in self._task_queue:
            coros.append(task.run())
        loop.run_until_complete(asyncio.wait(coros))

