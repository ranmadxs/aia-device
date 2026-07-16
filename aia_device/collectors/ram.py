"""RAM collector: usado/total, % y temperatura de DIMM (N/A si no hay sensor)."""
import psutil

from aia_utils.logs_cfg import config_logger

import logging

config_logger()
logger = logging.getLogger(__name__)


def collect() -> dict:
    vm = psutil.virtual_memory()
    total_gb = vm.total / (1024**3)
    used_gb = vm.used / (1024**3)
    # El i3-4150 / MSI H81M-E33 usualmente NO expone sensor de DIMM.
    return {
        "total_gb": round(total_gb, 1),
        "used_gb": round(used_gb, 1),
        "usage_percent": round(vm.percent, 1),
        "temp_c": None,  # N/A: sin sensor de DIMM
    }
