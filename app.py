from flask import Flask, render_template, jsonify, request, abort
from json import dumps, loads
from time import time, sleep
from vedis import Vedis
from threading import Thread
import schedule
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
from uuid import uuid1

db = Vedis("test.db")
app = Flask(__name__)

# how long to wait for check ins before aborting a protcol
TIMEOUT = 60

def broadcast_ip(key="flow_chemistry", port=1636):
    '''send out the location of our server'''
    s = socket(AF_INET, SOCK_DGRAM) # create UDP socket
    s.bind(('', 0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) # this is a broadcast socket
    my_ip = gethostbyname(gethostname()) # get our IP
    data = key + my_ip
    s.sendto(data.encode(), ('<broadcast>', port))
    print(f"Broadcasted IP {my_ip} with key {key} on port {port}")

def run_schedule():
    while True:
        schedule.run_pending()
        sleep(2.5) 

@app.route("/")
def index():
    return render_template("index.html")

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

    # if no protocol has been given, return Null
    except KeyError:
        return "no protocol"

@app.route("/start_time", methods=["GET"])
def start_time():
    with db.transaction():
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
            
        else:
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

if __name__ == "__main__":
    schedule.every(5).seconds.do(broadcast_ip)
    t = Thread(target=run_schedule)
    t.start()
    app.run(debug=True, host="0.0.0.0", use_reloader=True, threaded=True)
