"""Power collector: Total Watts = CPU (RAPL) + GPU (nvidia-smi power.draw).

Consumo de componentes, NO de la pared (eso requiere smart plug).
CPU: /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj (µJ acumulado).
Delta de energía / 1s = Watts.
"""
import time

from aia_utils.logs_cfg import config_logger

import logging

config_logger()
logger = logging.getLogger(__name__)

RAPL_PATH = "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"

_state = {"last_uj": None, "last_ts": None}


def _read_rapl_uj() -> int | None:
    try:
        with open(RAPL_PATH) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError, OSError) as e:
        logger.debug(f"RAPL no disponible: {e}")
        return None


def cpu_watts() -> float | None:
    now_uj = _read_rapl_uj()
    now_ts = time.time()
    if now_uj is None or _state["last_uj"] is None:
        _state["last_uj"] = now_uj
        _state["last_ts"] = now_ts
        return None
    dt = now_ts - _state["last_ts"]
    du = now_uj - _state["last_uj"]
    _state["last_uj"] = now_uj
    _state["last_ts"] = now_ts
    if dt <= 0 or du < 0:
        return None
    return round(du / 1_000_000 / dt, 1)


def collect(gpu_power_w: float | None) -> dict:
    cpu_w = cpu_watts()
    gpu_w = gpu_power_w if gpu_power_w is not None else None
    total = None
    if cpu_w is not None and gpu_w is not None:
        total = round(cpu_w + gpu_w, 1)
    return {
        "cpu_w": cpu_w,
        "gpu_w": gpu_w,
        "total_w": total,
    }
