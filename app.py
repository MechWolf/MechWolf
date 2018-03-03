from flask import Flask, render_template, jsonify, request, abort
from json import dumps, loads
from time import time, sleep
from vedis import Vedis
from threading import Thread
import schedule
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
from logging.config import dictConfig

db = Vedis("test.db")
app = Flask(__name__)

# how long to wait for check ins before aborting a protcol
TIMEOUT = 60

def broadcast_ip(key="flow_chemistry", port=1636):
    s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
    s.bind(('', 0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
    my_ip = gethostbyname(gethostname()) #get our IP. Be careful if you have multiple network interfaces or IPs
    data = key + my_ip
    s.sendto(data.encode(), ('<broadcast>', port))
    print("sent service announcement")

def run_schedule():
    while True:
        schedule.run_pending()
        sleep(2.5) 

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit_protcol", methods=["POST"])
def submit_protcol():
    '''accepts a protocol posted as a json'''
    with db.transaction():
        db["protocol"] = request.form.get("protocol_json")

        # clear the stored values when a new protocol comes in
        for i in range(len(db.Set("protocol_acks"))):
            db.Set("protocol_acks").pop()
        for i in range(len(db.Set("start_time_acks"))):
            db.Set("start_time_acks").pop()
        for i in range(db.llen("log")):
            db.lpop("log")
        try:
            del db["start_time"]
        except KeyError:
            pass

        # store the time when the protocol came in
        db["protocol_submit_time"] = time()

    return "accepted"

@app.route("/protocol", methods=["GET", "POST"])
def protocol():
    '''endpoint for devices to check for new protocols to be posted'''
    try:
        with db.transaction():
            # to allow easier introspection, let people view the protocol
            if request.method == "GET": 
                return jsonify(loads(db["protocol"]))

            # only give the protocol once
            if request.form["device_id"] in db.Set("protocol_acks"):
                return "no protocol"

            # store the device that checked in and and return the protocol
            db.Set("protocol_acks").add(request.form["device_id"])

            return app.response_class(
                response=dumps(loads(db["protocol"])[request.form.get("device_id")]),
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

@app.route("/log", methods=["POST"])
def log():
    with db.transaction():
        db.List("log").append(request.json)
    return "logged"

if __name__ == "__main__":
    schedule.every(5).seconds.do(broadcast_ip)
    t = Thread(target=run_schedule)
    t.start()
    app.run(debug=True, host="0.0.0.0", use_reloader=False)