from json import dumps, loads
from time import time, sleep
from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
from uuid import uuid1
import binascii

from flask import Flask, render_template, jsonify, request, abort
from vedis import Vedis
import schedule
import yaml
import rsa
import requests
from itsdangerous import Signer

import mechwolf as mw

config_db = Vedis("config.db")
db = Vedis("hub.db") # set up database
app = Flask(__name__) # create flask app

# how long to wait for check ins before aborting a protcol
TIMEOUT = 60

# get the config data
with open("hub_config.yml", "r") as f:
    config = yaml.load(f)
SECURITY_KEY = config['resolver_info']['security_key']
HUB_ID = config['resolver_info']['hub_id']

# get the private key
with open(config['resolver_info']['rsa_private_filepath'], mode='rb') as privatefile:
    keydata = privatefile.read()
PRIV_KEY = rsa.PrivateKey.load_pkcs1(keydata)

# get the public key
with open(config['resolver_info']['rsa_public_filepath'], mode='rb') as pubfile:
    keydata = pubfile.read()
# the inverse function call here is to verify that they public key is valid
PUB_KEY_HEX = binascii.hexlify(rsa.PublicKey.load_pkcs1(keydata).save_pkcs1()).decode()

def update_ip():
    '''send out the location of our server to the resolver if nescessary '''

    # find current IP address
    ip_socket = socket(AF_INET, SOCK_DGRAM)
    ip_socket.connect(("8.8.8.8", 80))
    my_ip = ip_socket.getsockname()[0]
    ip_socket.close()

    # return early if address on file matches
    try:
        if my_ip == config_db["current_ip"]:
            return
    except KeyError:
        pass

    # store new IP address
    with config_db.transaction():
        config_db["current_ip"] = my_ip

    # sign the current IP address
    s = Signer(SECURITY_KEY)
    signed_ip = s.sign(my_ip.encode())
    signature = rsa.sign(signed_ip, PRIV_KEY, 'SHA-512')
    signature = binascii.hexlify(signature).decode()

    # send it to the resolver
    payload = {"hub_id": HUB_ID,
               "hub_address": signed_ip,
               "hub_address_signature": signature,
               "hub_public_key": PUB_KEY_HEX}
    requests.post(mw.RESOLVER_URL + "register", data=payload)

    print(f"Updated resolver with IP {my_ip}.")

def run_schedule():
    while True:
        schedule.run_pending()
        sleep(2.5)

@app.route("/submit_protocol", methods=["POST"])
def submit_protocol():
    '''accepts a protocol posted as a json'''
    with db.transaction():
        db["protocol"] = request.form.get("protocol_json")
        db["protocol_id"] = str(uuid1())

        # clear the stored values when a new protocol comes in
        for i in range(len(db.Set("protocol_acks"))):
            db.Set("protocol_acks").pop()
        for i in range(len(db.Set("start_time_acks"))):
            db.Set("start_time_acks").pop()
        try:
            del db["start_time"]
        except KeyError:
            pass

        # store the time when the protocol came in
        db["protocol_submit_time"] = time()
        return jsonify(dict(protocol_id=db["protocol_id"]))

@app.route("/protocol", methods=["GET", "POST"])
def protocol():
    '''endpoint for devices to check for new protocols to be posted'''
    try:
        with db.transaction():

            # load the protocol and add the protocol_id
            parsed_protocol = loads(db["protocol"])
            parsed_protocol.update({"protocol_id": db["protocol_id"]})

            device_id = request.form["device_id"]

            # to allow easier introspection, let people view the protocol
            if request.method == "GET":
                return jsonify(parsed_protocol)

            # only give the protocol once
            if device_id in db.Set("protocol_acks"):
                return "no protocol"

            # store the device that checked in and and return the protocol
            db.Set("protocol_acks").add(device_id)

            return app.response_class(
                response=dumps({k: parsed_protocol[k] for k in ["protocol_id", device_id]}),
                status=200,
                mimetype="application/json")

    # if no protocol has been given
    except KeyError:
        return "no protocol"

@app.route("/start_time", methods=["GET"])
def start_time():
    with db.transaction():
        try:
            # time out if too long has passed from when the protocol was submitted but not all devices have checked in
            if time() - float(db["protocol_submit_time"]) > TIMEOUT:
                return "abort"

            # if every device has gotten the protocol, give them the start time
            if all([x in db.Set("protocol_acks") for x in list(loads(db["protocol"]))]):

                if request.args["device_id"] in db.Set("start_time_acks"):
                    return "no start time"

                # try to log the device ID but fail gracefully if not provided to allow introspection
                try:
                    db.Set("start_time_acks").add(request.args["device_id"])
                except KeyError:
                    pass

                # the first device after all have checked in will determine start time
                try:
                    return db["start_time"]
                except KeyError:
                    db["start_time"] = time() + 5
                    return db["start_time"]

        except KeyError:
            pass
        return "no start time"

@app.route("/log", methods=["POST", "GET"])
def log():
    print(f"Logging {request.json}")
    with db.transaction():
        if request.method == "GET":
            return jsonify([loads(x) for x in list(db.List("log"))])
            return str(list(db.List("log")))
        db.List("log").append(request.json)
    return "logged"


schedule.every(5).seconds.do(update_ip)
t = Thread(target=run_schedule)
t.start()
app.run(debug=True, host="0.0.0.0", use_reloader=True, threaded=True, port=80)
