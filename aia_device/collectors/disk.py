"""Disk collector: uso de /, I/O MB/s y temperatura SMART (Temperature_Celsius)."""
import re
import subprocess

import psutil

from aia_utils.logs_cfg import config_logger

import logging

config_logger()
logger = logging.getLogger(__name__)

ROOT = "/"
DEVICE = "/dev/sda"


def _io_mbps() -> dict:
    try:
        io1 = psutil.disk_io_counters()
        t1 = psutil.time.time()
        import time

        time.sleep(1)
        io2 = psutil.disk_io_counters()
        t2 = psutil.time.time()
        dt = max(t2 - t1, 0.001)
        read_mb = (io2.read_bytes - io1.read_bytes) / 1_000_000 / dt
        write_mb = (io2.write_bytes - io1.write_bytes) / 1_000_000 / dt
        return {"read_mbps": round(read_mb, 1), "write_mbps": round(write_mb, 1)}
    except Exception as e:
        logger.debug(f"disk io no disponible: {e}")
        return {"read_mbps": None, "write_mbps": None}


def _model() -> dict:
    """Marca/modelo del disco vía smartctl (si está disponible)."""
    try:
        out = subprocess.run(
            ["smartctl", "-i", DEVICE], capture_output=True, text=True, timeout=5
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug(f"smartctl no disponible: {e}")
        return {"brand": None, "model": None}
    brand = model = None
    for line in out.stdout.splitlines():
        s = line.strip()
        if s.startswith("Model Family:"):
            brand = s.split(":", 1)[1].strip() or None
        elif s.startswith("Device Model:"):
            model = s.split(":", 1)[1].strip() or None
    if not brand and model:
        brand = model.split()[0]
    return {"brand": brand, "model": model}


def _smart_temp() -> float | None:
    try:
        out = subprocess.run(
            ["smartctl", "-A", DEVICE], capture_output=True, text=True, timeout=5
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug(f"smartctl no disponible: {e}")
        return None
    for line in out.stdout.splitlines():
        if "Temperature_Celsius" in line:
            m = re.search(r"(\d+)\s*$", line.strip())
            if m:
                return float(m.group(1))
    return None


def collect() -> dict:
    usage = psutil.disk_usage(ROOT)
    total_gb = usage.total / (1024**3)
    used_gb = usage.used / (1024**3)
    io = _io_mbps()
    model = _model()
    return {
        "mount": ROOT,
        "device": DEVICE,
        "brand": model.get("brand"),
        "model": model.get("model"),
        "total_gb": round(total_gb, 1),
        "used_gb": round(used_gb, 1),
        "usage_percent": round(usage.percent, 1),
        "read_mbps": io["read_mbps"],
        "write_mbps": io["write_mbps"],
        "temp_c": _smart_temp(),
    }
