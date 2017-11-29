from flask import Flask, jsonify, render_template, request, url_for, session, redirect, flash
app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route('/log', methods=["POST"])
def log():
    with open("data.csv", "a+") as f:
    	print(request.time, request.instrument, request.data, sep=",", file=f)

if __name__ == '__main__':
	app.run()