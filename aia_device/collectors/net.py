"""Network collector: ancho de banda RX/TX por interfaz + ruta por defecto."""
import psutil

from aia_utils.logs_cfg import config_logger

import logging

config_logger()
logger = logging.getLogger(__name__)

# Interfaces de interés en nara (enp2s0 DOWN, wlx0013eff21155 UP).
WATCH = ["enp2s0", "wlx0013eff21155", "docker0", "vxlan.calico"]


def _default_iface() -> str | None:
    """Lee la ruta por defecto desde /proc/net/route (no depende de `ip`).

    En /proc/net/route la columna 0 es el NOMBRE de la interfaz (no el índice).
    """
    try:
        with open("/proc/net/route") as f:
            next(f)  # header
            for line in f:
                parts = line.split()
                # Destination 00000000 (0.0.0.0) + flags con RTF_UP|RTF_GATEWAY
                # (0x001 = UP, 0x002 = GATEWAY => 0x003). Algunos kernels reportan
                # solo 0x002; aceptamos ambos para robustez.
                if parts[1] == "00000000" and parts[3] in ("0002", "0003"):
                    return parts[0]
    except OSError as e:
        logger.debug(f"/proc/net/route no disponible: {e}")
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
