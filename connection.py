# connection.py 
# Manages connection to AWS IoT
# Todo: Use Asyncio so that message waiting does not block.
# Todo: define schema and use to validate json
# Todo: add unit test
# from connection import Connection
# c = Connection()
# c.add_object('test')
# c.connected('test')
# Should return false
# c.client.publish('test','{"connected":1}',1)
# c.connected('test')
# should return true

from AWSIoTPythonSDK import MQTTLib
import json

class Connection:

    def __init__(self, certificate = 'cert/aws_root_auth.pem', 
                       endpoint_url = 'a365awttlmyft7.iot.us-east-1.amazonaws.com'): 
        
        self.objects = {}
        self.client = MQTTLib.AWSIoTMQTTClient('server',useWebsocket=True)
        self.client.configureCredentials('cert/aws_root_auth.pem')
        self.client.configureEndpoint(endpoint_url,443)
        self.client.connect()

    def _add_object(self, object_id, quality_of_service = 0):
        
        if self.client.subscribe(object_id, quality_of_service, self.on_message):
            self.objects[object_id] = {'connected': False}
            if not self.client.publish(object_id, '{"ping":1}', 1):
                raise RuntimeError('Unable to send message')
        else:
            raise RuntimeError('Unable to subscribe to topic')

    def on_message(self, client, userdata, message):
        object_id = message.topic
        try:
            message_content = json.loads(message.payload)
        except:
            raise Warning('Received message contained invalid json')
            return

        if 'connected' in message_content:
            if object_id in self.objects:
                self.objects[object_id]['connected'] = True
        elif 'some other keyword' in message_content:
            pass

    def connected(self, object_id):
        if object_id in self.objects:
            return self.objects[object_id]['connected']
        else:
            return False
