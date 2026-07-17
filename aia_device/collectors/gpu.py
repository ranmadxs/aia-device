"""GPU collector: NVIDIA RTX 3060 vía nvidia-smi (uso, VRAM, watts, temp, límite)."""
import subprocess

from aia_utils.logs_cfg import config_logger

import logging

config_logger()
logger = logging.getLogger(__name__)

QUERY = (
    "utilization.gpu,memory.used,memory.total,power.draw,power.limit,"
    "temperature.gpu"
)
FORMAT = "csv,noheader,nounits"


def _name() -> str | None:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip().splitlines()[0] or None
    except (FileNotFoundError, subprocess.TimeoutExpired, IndexError) as e:
        logger.debug(f"nvidia-smi name no disponible: {e}")
        return None


def _query() -> list[float]:
    out = subprocess.run(
        ["nvidia-smi", f"--query-gpu={QUERY}", f"--format={FORMAT}"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    line = out.stdout.strip().splitlines()[0]
    return [float(x) for x in line.split(",")]


def collect() -> dict:
    try:
        name = _name()
        util, mem_used, mem_total, power, power_limit, temp = _query()
    except (FileNotFoundError, subprocess.TimeoutExpired, IndexError, ValueError) as e:
        logger.debug(f"nvidia-smi no disponible: {e}")
        return {
            "available": False,
            "brand": "NVIDIA",
            "model": None,
            "usage_percent": None,
            "mem_used_mb": None,
            "mem_total_mb": None,
            "power_w": None,
            "power_limit_w": None,
            "temp_c": None,
        }
    return {
        "available": True,
        "brand": "NVIDIA",
        "model": name,
        "usage_percent": round(util, 1),
        "mem_used_mb": round(mem_used),
        "mem_total_mb": round(mem_total),
        "power_w": round(power, 1),
        "power_limit_w": round(power_limit, 1),
        "temp_c": round(temp, 1),
    }
