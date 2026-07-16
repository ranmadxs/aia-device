"""Network collector: ancho de banda RX/TX por interfaz + ruta por defecto."""
import subprocess

import psutil

from aia_utils.logs_cfg import config_logger

import logging

config_logger()
logger = logging.getLogger(__name__)

# Interfaces de interés en nara (enp2s0 DOWN, wlx0013eff21155 UP).
WATCH = ["enp2s0", "wlx0013eff21155", "docker0", "vxlan.calico"]


def _default_iface() -> str | None:
    try:
        out = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for tok in out.stdout.split():
            if tok == "dev":
                return None  # el siguiente token es la iface
        # Forma simple: buscar 'dev <iface>'
        parts = out.stdout.split()
        if "dev" in parts:
            return parts[parts.index("dev") + 1]
    except (FileNotFoundError, subprocess.TimeoutExpired, IndexError, ValueError) as e:
        logger.debug(f"ip route no disponible: {e}")
    return None


def collect() -> dict:
    counters1 = psutil.net_io_counters(pernic=True)
    import time

    time.sleep(1)
    counters2 = psutil.net_io_counters(pernic=True)
    default = _default_iface()
    interfaces = {}
    for name in list(counters1.keys()):
        if WATCH and name not in WATCH and name != default:
            continue
        c1 = counters1[name]
        c2 = counters2.get(name)
        if c2 is None:
            continue
        dt = 1.0
        rx_kbps = (c2.bytes_recv - c1.bytes_recv) / 1024 / dt
        tx_kbps = (c2.bytes_sent - c1.bytes_sent) / 1024 / dt
        interfaces[name] = {
            "rx_kbps": round(rx_kbps, 1),
            "tx_kbps": round(tx_kbps, 1),
            "is_default": name == default,
        }
    return {"default_iface": default, "interfaces": interfaces}
