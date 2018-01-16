from MQTTLib import AWSIoTMQTTClient
import time
import awsconfig
import json


# user specified callback function
def customCallback(client, userdata, message):
	print("Received a new message: ")
	message = json.loads(message.payload)
	for key,value in message.items():
		print(key,value)

time.sleep(5)
# awsconfigure the MQTT client
pycomAwsMQTTClient = AWSIoTMQTTClient(awsconfig.CLIENT_ID)
pycomAwsMQTTClient.configureEndpoint(awsconfig.AWS_HOST, awsconfig.AWS_PORT)
pycomAwsMQTTClient.configureCredentials(awsconfig.AWS_ROOT_CA, awsconfig.AWS_PRIVATE_KEY, awsconfig.AWS_CLIENT_CERT)

pycomAwsMQTTClient.configureOfflinePublishQueueing(awsconfig.OFFLINE_QUEUE_SIZE)
pycomAwsMQTTClient.configureDrainingFrequency(awsconfig.DRAINING_FREQ)
pycomAwsMQTTClient.configureConnectDisconnectTimeout(awsconfig.CONN_DISCONN_TIMEOUT)
pycomAwsMQTTClient.configureMQTTOperationTimeout(awsconfig.MQTT_OPER_TIMEOUT)
pycomAwsMQTTClient.configureLastWill(awsconfig.LAST_WILL_TOPIC, awsconfig.LAST_WILL_MSG, 1)

#Connect to MQTT Host
if pycomAwsMQTTClient.connect():
    print('AWS connection succeeded')
else:
	print("Oops...")
# Subscribe to topic
pycomAwsMQTTClient.subscribe(awsconfig.TOPIC, 1, customCallback)
time.sleep(2)


