from flask import Flask, render_template, jsonify, request, abort
import json
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
    for i in range(len(db.Set("acks") )):
        db.Set("acks").pop()

    return "accepted"

@app.route("/protocol", methods=["POST"])
def protocol():
    '''endpoint for devices to check for new protocols to be posted'''

    # once every device has gotten the protocol, give them the start time
    if all([x in db.Set("acks") for x in list(json.loads(db["protocol"]))]):
        try:
            return db["start_time"]
        except KeyError:
            db["start_time"] = time() + 15
            return db["start_time"]

    # store the device that checked in and got the protocol
    db.Set("acks").add(request.form["device_id"])

    return app.response_class(
        response=json.dumps(json.loads(db["protocol"])[request.form.get("device_id")]),
        status=200,
        mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)