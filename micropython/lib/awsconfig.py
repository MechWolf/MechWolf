# wifi configuration
WIFI_SSID = 'my_wifi_ssid'
WIFI_PASS = 'my_wifi_password'

# AWS general configuration
AWS_PORT = 8883
AWS_HOST = 'a365awttlmyft7.iot.us-east-1.amazonaws.com'
AWS_ROOT_CA = '/flash/cert/root-ca.pem'
AWS_CLIENT_CERT = '/flash/cert/certificate.crt'
AWS_PRIVATE_KEY = '/flash/cert/privateKey.key'

################## Subscribe / Publish client #################
CLIENT_ID = 'pump0'
TOPIC = 'pump0'
OFFLINE_QUEUE_SIZE = -1
DRAINING_FREQ = 2
CONN_DISCONN_TIMEOUT = 10
MQTT_OPER_TIMEOUT = 5
LAST_WILL_TOPIC = 'pump0'
LAST_WILL_MSG = 'To All: Last will message'