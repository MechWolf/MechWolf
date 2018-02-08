from MQTTLib import AWSIoTMQTTClient
import time
import awsconfig
import json
from machine import Pin
import _thread

# Method Object
# [{'params': {'cmd1':[**args]...} 'start_time':'hh:mm:ss', 'stop_time':'hh:mm:ss'}
#  {'params': .....}]

# user specified callback function
def messageReceived(client, userdata, message):
    print("Received a new message: ")

    try:
        message = json.loads(message.payload)
    except ValueError as err:
        raise Warning("Json Error: {0}".format(err))
        return False
    print(message)

    if 'time' in message:
        time = message['time']
    
    if 'task_id' in message:
        task_id = message['task_id']
        if 'run' in message:
            client.publish('server',json.dumps({'task_id':task_id, 'state':'RUNNING'}), qos = 1, retain = 0)
            run()
            client.publish('server',json.dumps({'task_id':task_id, 'state':'FINISHED'}), qos = 1, retain = 0)
            return True
        #pass the remaining arguments to the execute function
        if add_task(client, task_id, time, **message['params']):
            #Reply that the command was received.
            client.publish('server',json.dumps({'task_id':task_id, 'state':'RECEIVED'}), qos = 1, retain = 0)
    gc.collect()
    return True

def add_task(client, task_id, time, **kwargs):
    #TODO: Make sure tasks that are sent twice don't get added twice!!
    global tasks

    if 'active' in kwargs:
        params = kwargs['active']
        tasks[task_id] = {'function': active, 'params': params, 'time': time, 'client':client}
        return True

def active(value):
    #Switches the LED to the value specified.
    if p10.value() == value:
        return
    else:
        p10.toggle()

def run():
    #todo: add stop check
    global tasks
    start_time = time.time()
    completed_tasks = []

    while tasks:
        for task_id,task in tasks.items():
            if time.time() - start_time >= task['time']:
                function = task['function']
                params = task['params']
                client = task['client']
                print(function,params)
                function(params)
                #TODO: Replace this with a function call to change a task state
                client.publish('server',json.dumps({'task_id':task_id, 'state':'COMPLETE'}), qos = 1, retain = 0)
                print('debug')
                completed_tasks.append(task_id)
        for task_id in completed_tasks:
            tasks.pop(task_id)
            completed_tasks = []


def test(client, userdata, message):
    global tasks
    message = json.loads(message.payload)
    tasks[message['task_id']] = message
    gc.collect()

def awsconfigure():
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
        print("Connection Failed")
    # Subscribe to topic
    print('subscribing to topic', awsconfig.TOPIC)
    pycomAwsMQTTClient.subscribe(awsconfig.TOPIC, 1, messageReceived)
    return pycomAwsMQTTClient

global tasks
global stop_flag
global is_running

stop_flag = False
is_running = False
tasks = {}
gc.enable()
time.sleep(5)

p10 = Pin('P10',Pin.OUT,Pin.PULL_UP)
client = awsconfigure()
