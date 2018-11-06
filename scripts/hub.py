import json
from time import time, sleep
from uuid import uuid1
import shelve
import logging

from flask import Flask, render_template, jsonify, request, abort
import schedule
import yaml
from pathlib import Path

import mechwolf as mw

logging.getLogger("schedule").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.INFO)

app = Flask(__name__, static_folder="vis/",
                      template_folder="vis/",
                      static_url_path="")
 # create flask app

# how long to wait for check ins before aborting a protcol
TIMEOUT = 60

# get the config data
with open("hub_config.yml", "r") as f:
    config = yaml.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit_protocol", methods=["POST"])
def submit_protocol():
    '''Accepts a protocol posted as JSON.'''
    logging.info("Received protocol")
    with shelve.open('hub') as db:

        # check to see if a protocol is being executed
        try:
            if time() - float(db["start_time"]) < db["duration"]:
                logging.warning("Attempting to start protocol while one is being executed")
                return "protocol rejected: different protocol being executed"
            else:
                logging.debug("No protocol is being executed.")
        except KeyError:
            logging.debug("No recorded start time/duration")
            pass

        protocol = json.loads(request.form.get("protocol"))

        # calculate the duration of the protocol in seconds
        duration = 0
        for i in range(len(protocol)):
            component_duration = max([x["time"] for x in list(protocol.values())[i]])
            if component_duration > duration:
                duration = component_duration
        db["duration"] = duration

        db["protocol_devices"] = list(protocol.keys())
        db["protocol"] = request.form.get("protocol")
        protocol_id = str(uuid1())
        db["protocol_id"] = protocol_id

        # clear the stored values when a new protocol comes in
        db["protocol_acks"] = set()
        db["start_time_acks"] = set()
        try:
            del db["start_time"]
        except KeyError:
            pass

        # store the time when the protocol came in
        db["protocol_submit_time"] = time()

        with shelve.open(f'experiments/{ db["protocol_id"] }') as protocol_db:
            protocol_db["protocol"] = protocol
            protocol_db["protocol_id"] = protocol_id
            protocol_db["protocol_submit_time"] = db["protocol_submit_time"]

        return db["protocol_id"]


@app.route("/protocol")
def protocol():
    '''Returns protocols, if availible.'''
    try:
        with shelve.open('hub') as db:

            # load the protocol and add the protocol_id
            protocol = dict(protocol=db["protocol"])
            protocol.update({"protocol_id": db["protocol_id"]})

            # to allow easier introspection, let people view the protocol
            if not request.args:
                return jsonify(protocol)

            # only give the protocol once
            try:
                if request.args["device_id"] in db["protocol_acks"]:
                    return "no protocol"
            except KeyError:
                pass

            # store the device that checked in and and return the protocol
            db["protocol_acks"] = db["protocol_acks"].union([request.args["device_id"]])

            return jsonify(protocol)

    # if no protocol has been given
    except KeyError:
        return "no protocol"


@app.route("/start_time")
def start_time():
    with shelve.open('hub') as db:
        try:
            # time out if too long has passed from when the protocol was
            # submitted but not all devices have checked in
            logging.debug("Checking to see if timing out...")
            if time() - float(db["protocol_submit_time"]) > TIMEOUT:
                return "abort"
            logging.debug("Not timing out")

            device_id = request.args.get("device_id")

            # if every device has gotten the protocol, give them the start time
            logging.debug(
                f'Checking if all of {db["protocol_acks"]} are in {db["protocol_devices"]}.')
            if all([x in db["protocol_acks"] for x in db["protocol_devices"]]):
                logging.debug("They are!")

                # log the device ID as having gotten start time
                if device_id in db["start_time_acks"]:
                    return "no start time"
                elif device_id is not None:
                    db["start_time_acks"] = db["start_time_acks"].union([device_id])

                logging.debug(
                    f"List of acknowledged start times is now {db['start_time_acks']}")

                # the first device after all have checked in will determine
                # start time
                try:
                    return db["start_time"]
                except KeyError:
                    if request.args.get(
                            "device_id") is not None:  # return "no start time" if a blank request is gotten
                        logging.debug("No start time set. Setting new one...")
                        db["start_time"] = str(time() + 5)
                        logging.debug(f'Start time is {db["start_time"]}')
                        return db["start_time"]

        except KeyError:
            pass
        return "no start time"


@app.route("/log", methods=["POST", "GET"])
def log():
    logging.info(f"Logging {request.json['data']}")
    with shelve.open('hub') as db:
        protocol_id = db["protocol_id"]
    with shelve.open(f'experiments/{protocol_id}') as db:
        if request.method == "GET":
            try:
                return str(db["log"])
            except KeyError:
                return "no log"
        submission = json.loads(request.json["data"])
        try:
            db["data"] = db["data"] + [submission]
        except KeyError:
            db["data"] = []
    return "logged"

@app.route("/experiments", methods=["GET"])
def experiments():
    expts_folder = Path.cwd()/'experiments'
    expts = [file.name for file in expts_folder.iterdir()]
    return jsonify(expts)
# app.run(debug=False, host="0.0.0.0", use_reloader=True, threaded=True, port=80, ssl_context=('cert.pem', 'key.pem'))

@app.route("/experiments/<uuid:expt_id>", methods=["GET"])
def data(expt_id):
    expts_folder = Path.cwd()/'experiments'
    expt_path = expts_folder/str(expt_id)
    expts = [file for file in expts_folder.iterdir()]
    if expt_path in expts:
        with shelve.open(str(expt_path)) as db:
            return(jsonify(dict(db)))
    else:
        return(f"Experiment {expt} not found")
