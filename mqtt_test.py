#A test script for connecting to our mqtt server and dealing with messages.
#Before running, set your environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to their corresponding values from the keys file. os.environ["AWS_ACCESS_KEY_ID"] should return this value.

from AWSIoTPythonSDK import MQTTLib

def onMessage(client,userdata,message):
    print(message.topic,message.payload)

client = MQTTLib.AWSIoTMQTTClient('server',useWebsocket=True)
client.configureCredentials('aws_root_auth.pem')
client.configureEndpoint('a365awttlmyft7.iot.us-east-1.amazonaws.com',443)
client.connect()
client.subscribe('pump0',0,onMessage)
