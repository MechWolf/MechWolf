import json
import logging
import shelve
import webbrowser
from pathlib import Path
from time import sleep, time
from uuid import uuid1

import schedule
import yaml
from flask import Flask, abort, jsonify, render_template, request
from flask_socketio import SocketIO, emit

import mechwolf as mw

logging.getLogger("schedule").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.INFO)

app = Flask(__name__, static_folder="vis/",
            template_folder="vis/",
            static_url_path="")
# create flask app
socketio = SocketIO(app)

# how long to wait for check ins before aborting a protcol
TIMEOUT = 60

@app.route('/vis/<path:path>')
def any_root_path(path):
    return render_template('index.html')

@app.route("/vis/")
def index():
    return render_template("index.html")

@app.route("/log_procedure", methods=["POST", "GET"])
def log_procedure():
    logging.info(f"Logging procedure {request.json}")
    submission = json.loads(request.json)["procedure"]
    experiment_id = json.loads(request.json)["experiment_id"]

    with shelve.open(f'experiments/{experiment_id}') as db:
        if request.method == "GET":
            try:
                return str(db["log"])
            except KeyError:
                return "no log"

        if "logs" in db:
            logs = db["logs"]
            logs.append(submission)
            db["logs"] = logs
        else:
            db["logs"] = [submission]
        socketio.emit(f'log/{experiment_id}', submission)
        return "logged"

@app.route("/log_data", methods=["POST", "GET"])
def log_data():
    logging.info(f"logging data {request.json}")
    d = json.loads(request.json)
    datapoint = d["datapoint"]
    timestamp = d["timestamp"]
    device_id = d["device_id"]
    experiment_id = d["experiment_id"]

    to_log = {"data": datapoint,
              "timestamp": timestamp,
              "device_id": device_id}

    with shelve.open(f'experiments/{experiment_id}') as db:
        if "data" in db:
            data = db["data"]
            data.append(to_log)
            db["data"] = data
        else:
            db["data"] = [to_log]
        socketio.emit(f'data/{experiment_id}', to_log)
        return "logged"

@app.route("/log_start", methods=["POST", "GET"])
def log_start():
    d = json.loads(request.json)
    protocol = d["protocol"]
    protocol_start_time = d["protocol_start_time"]
    experiment_id = d["experiment_id"]
    with shelve.open(f'experiments/{experiment_id}') as db:
        db["protocol"] = protocol
        db["protocol_start_time"] = protocol_start_time
        db["protocol_id"] = experiment_id
    return "logged"

@app.route("/experiments", methods=["GET"])
def experiments():
    expts_folder = Path.cwd() / 'experiments'
    expts = [file.name for file in expts_folder.iterdir()]
    return jsonify(expts)
# app.run(debug=False, host="0.0.0.0", use_reloader=True, threaded=True, port=80, ssl_context=('cert.pem', 'key.pem'))

@app.route("/experiments/<expt_id>", methods=["GET"])
def data(expt_id):
    expts_folder = Path.cwd() / 'experiments'
    expt_path = expts_folder / expt_id
    expts = [file for file in expts_folder.iterdir()]
    if expt_path in expts:
        with shelve.open(str(expt_path)) as db:
            resp = dict(db)
            return(jsonify(resp))
    else:
        return(jsonify({'protocol_id': None}))

@app.route("/test/<msg>")
def test(msg):
    socketio.emit('test', msg)
    return msg
