from flask import Flask, render_template, jsonify, request, abort
from json import dumps, loads
from time import time
from vedis import Vedis

app = Flask(__name__)
db = Vedis("test.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit_protcol", methods=["POST"])
def submit_protcol():
    '''accepts a protocol posted as a json'''
    db["protocol"] = request.form.get("protocol_json")

    # clear the stored values when a new protocol comes in
    for i in range(len(db.Set("protocol_acks"))):
        db.Set("protocol_acks").pop()
    for i in range(len(db.Set("start_time_acks"))):
        db.Set("start_time_acks").pop()
    for i in range(db.llen("log")):
        db.lpop("log")
    del db["start_time"]

    return "accepted"

@app.route("/protocol", methods=["GET", "POST"])
def protocol():
    '''endpoint for devices to check for new protocols to be posted'''
    try:
        # to allow easier introspection, let people view the protocol
        if request.method == "GET": 
            return jsonify(loads(db["protocol"]))

        # only give the protocol once
        if request.form["device_id"] in db.Set("protocol_acks"):
            return "no protocol"

        # store the device that checked in and and return the protocol
        db.Set("protocol_acks").add(request.form["device_id"])
        print(dumps(loads(db["protocol"])[request.form.get("device_id")]))
        return app.response_class(
            response=dumps(loads(db["protocol"])[request.form.get("device_id")]),
            status=200,
            mimetype="application/json")

    # if no protocol has been given, return Null
    except KeyError:
        return "no protocol"

@app.route("/start_time", methods=["GET"])
def start_time():
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
    print(request.json)
    db.List("log").append(request.json)
    for i in db.List("log"):
        print(i)
    return "logged"

if __name__ == "__main__":
    app.run(debug=True)