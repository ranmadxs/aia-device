"""Flask app: dashboard en / y JSON en /api/metrics."""
import os

from flask import Flask, jsonify, render_template

from aia_device.monitor import monitor

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", port=os.getenv("PORT", "9006"))


@app.route("/api/metrics")
def metrics():
    return jsonify(monitor.snapshot())


def create_app() -> Flask:
    return app
