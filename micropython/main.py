import json
import time
import urequests as requests
import awsiot_sign
import machine

def timestamp():
	return "%04u%02u%02uT%02u%02u%02uZ" % time.localtime()[0:6]

def toggle(led):
	led.value(not led.value())

file = open('aws_info.txt')
keys = file.readline()
keys = json.loads(keys)
led = machine.Pin(0, machine.Pin.OUT)

while True:
	request_dict = awsiot_sign.request_gen(keys['endpt_prefix'], 'pump0', keys['akey'], keys['skey'], timestamp(), region=keys['region'], method='GET')
	endpoint = 'https://' + request_dict["host"] + request_dict["uri"]
	r = requests.get(endpoint, headers=request_dict["headers"])
	if r.status_code == 200:
		req = json.loads(r.text)
		if req['state']['desired']['light'] == led.value():
			toggle(led)
	time.sleep(1)