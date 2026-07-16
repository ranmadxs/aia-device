"""Orquestador de métricas: cachea el snapshot cada ~1-2 s bajo demanda."""
import threading
import time

from aia_utils.logs_cfg import config_logger

import logging

from aia_device.collectors import cpu, gpu, ram, disk, net, power, temps

config_logger()
logger = logging.getLogger(__name__)

_REFRESH_S = 1.5
_HISTORY_MAX = 180  # ~3 min a 1.5s de muestreo


def _extract_series(snap: dict) -> dict:
    """Extrae los valores escalares para la serie histórica."""
    return {
        "t": snap.get("timestamp"),
        "cpu_w": (snap.get("power") or {}).get("cpu_w"),
        "gpu_w": (snap.get("power") or {}).get("gpu_w"),
        "total_w": (snap.get("power") or {}).get("total_w"),
        "cpu_usage": (snap.get("cpu") or {}).get("usage_percent"),
        "gpu_usage": (snap.get("gpu") or {}).get("usage_percent"),
        "ram_usage": (snap.get("ram") or {}).get("usage_percent"),
        "cpu_temp": (snap.get("temps") or {}).get("cpu_c"),
        "gpu_temp": (snap.get("temps") or {}).get("gpu_c"),
    }


class Monitor:
    def __init__(self):
        self._lock = threading.Lock()
        self._snapshot = None
        self._ts = 0.0
        self._history = []

    def _build(self) -> dict:
        cpu_d = cpu.collect()
        gpu_d = gpu.collect()
        ram_d = ram.collect()
        disk_d = disk.collect()
        net_d = net.collect()
        pwr_d = power.collect(gpu_d.get("power_w"))
        temps_d = temps.collect(cpu_d, gpu_d, ram_d, disk_d)
        return {
            "timestamp": time.time(),
            "cpu": cpu_d,
            "gpu": gpu_d,
            "ram": ram_d,
            "disk": disk_d,
            "net": net_d,
            "power": pwr_d,
            "temps": temps_d,
        }

    def snapshot(self) -> dict:
        now = time.time()
        with self._lock:
            if self._snapshot is None or (now - self._ts) >= _REFRESH_S:
                try:
                    self._snapshot = self._build()
                    self._ts = now
                    self._history.append(_extract_series(self._snapshot))
                    if len(self._history) > _HISTORY_MAX:
                        self._history.pop(0)
                except Exception as e:  # nunca romper el dashboard
                    logger.error(f"error recolectando métricas: {e}")
                    if self._snapshot is None:
                        self._snapshot = {"error": str(e)}
        return self._snapshot

    def history(self) -> list:
        with self._lock:
            return list(self._history)


monitor = Monitor()
