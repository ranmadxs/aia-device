"""Flask app: dashboard en / y JSON en /api/metrics."""
import os

from flask import Flask, jsonify, render_template, request

from aia_device.monitor import Monitor

_HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(_HERE, "static"))
_monitor = None


def _get_monitor() -> Monitor:
    global _monitor
    if _monitor is None:
        _monitor = Monitor()
    return _monitor


@app.route("/")
def index():
    return render_template("index.html", port=os.getenv("PORT", "9006"))


@app.route("/api/metrics")
def metrics():
    return jsonify(_get_monitor().snapshot())


@app.route("/api/history")
def history():
    selected_range = request.args.get("range", "1h")
    return jsonify(_get_monitor().history(selected_range))


@app.route("/api/history_dates")
def history_dates():
    return jsonify(_get_monitor().history_dates())


def create_app() -> Flask:
    return app
