"""Orquestador de métricas: cachea el snapshot cada ~1-2 s bajo demanda."""
import threading
import time

from aia_utils.logs_cfg import config_logger

import logging

from aia_device.collectors import cpu, gpu, ram, disk, net, power, temps

config_logger()
logger = logging.getLogger(__name__)

_REFRESH_S = 1.5


class Monitor:
    def __init__(self):
        self._lock = threading.Lock()
        self._snapshot = None
        self._ts = 0.0

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
                except Exception as e:  # nunca romper el dashboard
                    logger.error(f"error recolectando métricas: {e}")
                    if self._snapshot is None:
                        self._snapshot = {"error": str(e)}
        return self._snapshot


monitor = Monitor()
