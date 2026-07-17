"""RAM collector: usado/total, % y temperatura de DIMM (N/A si no hay sensor)."""
import subprocess

import psutil

from aia_utils.logs_cfg import config_logger

import logging

config_logger()
logger = logging.getLogger(__name__)


def _model() -> dict:
    """Marca/modelo de la RAM vía dmidecode (si está disponible)."""
    try:
        out = subprocess.run(
            ["dmidecode", "--type", "memory"],
            capture_output=True, text=True, timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug(f"dmidecode no disponible: {e}")
        return {"brand": None, "model": None}
    brand = None
    for line in out.stdout.splitlines():
        s = line.strip()
        if s.startswith("Manufacturer:"):
            brand = s.split(":", 1)[1].strip() or None
        elif s.startswith("Part Number:") and brand:
            pn = s.split(":", 1)[1].strip()
            if pn and pn != "Not Specified":
                return {"brand": brand, "model": pn}
    return {"brand": brand, "model": None}


def collect() -> dict:
    vm = psutil.virtual_memory()
    total_gb = vm.total / (1024**3)
    used_gb = vm.used / (1024**3)
    # El i3-4150 / MSI H81M-E33 usualmente NO expone sensor de DIMM.
    model = _model()
    return {
        "total_gb": round(total_gb, 1),
        "used_gb": round(used_gb, 1),
        "usage_percent": round(vm.percent, 1),
        "temp_c": None,  # N/A: sin sensor de DIMM
        "brand": model.get("brand"),
        "model": model.get("model"),
    }
