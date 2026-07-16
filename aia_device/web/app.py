"""Flask app: dashboard en / y JSON en /api/metrics."""
import os

from flask import Flask, jsonify, render_template

from aia_device.monitor import monitor

_HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(_HERE, "static"))


@app.route("/")
def index():
    return render_template("index.html", port=os.getenv("PORT", "9006"))


@app.route("/api/metrics")
def metrics():
    return jsonify(monitor.snapshot())


@app.route("/api/history")
def history():
    return jsonify(monitor.history())


def create_app() -> Flask:
    return app
