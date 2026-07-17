"""CPU collector: uso %, load average, núcleos/hilos, marca/modelo y temperatura."""
import os
import re
import subprocess

import psutil

from aia_utils.logs_cfg import config_logger

import logging

config_logger()
logger = logging.getLogger(__name__)

SENSORS_LABEL = "Package id 0"


def _model() -> dict:
    """Marca/modelo del CPU vía /proc/cpuinfo (brand, name, cores físicos)."""
    try:
        with open("/proc/cpuinfo") as fh:
            info = fh.read()
        brand, name, vendor = None, None, None
        for line in info.splitlines():
            if line.startswith("vendor_id"):
                vendor = line.split(":", 1)[1].strip()
            elif line.startswith("model name"):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("Hardware") and not brand:
                brand = line.split(":", 1)[1].strip()
        if name:
            if vendor == "GenuineIntel":
                brand = "Intel"
            elif vendor == "AuthenticAMD":
                brand = "AMD"
        return {"brand": brand, "model": name}
    except Exception as e:
        logger.debug(f"cpu model no disponible: {e}")
        return {"brand": None, "model": None}


def _read_sensors_temp() -> float | None:
    """Lee la temperatura del Package id 0 desde `sensors` (coretemp)."""
    try:
        out = subprocess.run(["sensors"], capture_output=True, text=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug(f"sensors no disponible: {e}")
        return None
    for line in out.stdout.splitlines():
        if SENSORS_LABEL in line:
            m = re.search(r"([+-]?\d+(?:\.\d+)?)°C", line)
            if m:
                return float(m.group(1))
    return None


def collect() -> dict:
    load1, load5, load15 = os.getloadavg()
    cpu_percent = psutil.cpu_percent(interval=0.2)
    cores = psutil.cpu_count(logical=False) or 0
    threads = psutil.cpu_count(logical=True) or 0
    temp = _read_sensors_temp()
    model = _model()
    return {
        "usage_percent": round(cpu_percent, 1),
        "load": {"1": round(load1, 2), "5": round(load5, 2), "15": round(load15, 2)},
        "cores": cores,
        "threads": threads,
        "temp_c": temp,
        "brand": model.get("brand"),
        "model": model.get("model"),
    }
