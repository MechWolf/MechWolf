# connection.py 
# Manages connection to AWS IoT

import uuid
from concurrent.futures import _base
from AWSIoTPythonSDK import MQTTLib
from collections import deque
import json

class _DeviceWorkItem(object):
    def __init__(self, *, future, device_id, task_id, kwargs):
        self.future = future
        self.device_id = device_id
        self.task_id = task_id
        self.kwargs = kwargs

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return

    #TODO Fill in the rest here

class DeviceExecutor(_base.Executor):

    def __init__(self, connection=None):
        self.connection=connection
        self._task_queue = deque()

    def submit(self, device_id, *args, **kwargs):
        task_id = uuid.uuid1().hex
        f = _base.Future()
        self._task_queue.append(_DeviceWorkItem(future=f, device_id=device_id, task_id=task_id, kwargs=kwargs))
        self.send_to_devices()
        return f

    def send_to_devices(self):
        for task in self._task_queue:
            if task.future._state == 'PENDING':
                self.connection.send(device_id=task.device_id, task_id=task.task_id, message=task.kwargs, callback=self.state_callback)

    def state_callback(self, task_id, state):
        #Optimize?
        for task in self._task_queue:
            if task.task_id == task_id:
                task.future._state = state
        

class Connection(object):
    # Manages the connection to the AWS message broker.
    def __init__(self, certificate='cert/aws_root_auth.pem', endpoint_url='a365awttlmyft7.iot.us-east-1.amazonaws.com'): 
        self.components = {}
        self.client = MQTTLib.AWSIoTMQTTClient('server', useWebsocket=True)
        self.client.configureCredentials(certificate)
        self.client.configureEndpoint(endpoint_url, 443)
        self.tasks = {}
        
    def connect(self):
        self.client.connect()  
        if not self.client.subscribe('server', 1, self.on_message):
            raise RuntimeError("Unable to subscribe to server topic")

    def register(self, *, task_id, callback):
        if task_id in self.tasks:
            return False
        else:
            self.tasks[task_id] = callback
            return True

    def send(self, device_id, task_id, message, callback):
        
        self.register(task_id = task_id, callback = callback)

        if not self.client.publish(device_id, json.dumps(dict(task_id=task_id, device_id=device_id)), 1):
            raise RuntimeError('unable to send message')

        return True

    
    def on_message(self, client, userdata, message):
        try:
            message_content = json.loads(message.payload)
            device_id = message_content['device_id']
        except:
            raise Warning('Received message contained invalid json or did not contain device_id key.')
        
        if 'task_id' and 'state' in message_content:
            task_id = message_content['task_id']
            state = message_content['state']
            print('received task update!')
            callback = self.tasks[task_id]
            callback(task_id, state)

        if 'connected' in message_content:
            if component_name in self.components:
                self.components[component_name].connected = True
        elif 'some other keyword' in message_content:
            pass

    def is_connected(self, component):
        if component.name in self.components:
            return self.components[component.name].connected
        return False

    def _connect_component(self, component, quality_of_service=0):
        self.components[component.name] = component
        if not self.client.publish(component.name, '{"ping":1}', 1):
            raise RuntimeError('Unable to send message')

