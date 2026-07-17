"""Top processes collector: top 10 por uso de CPU y de RAM (psutil)."""
import psutil

from aia_utils.logs_cfg import config_logger

import logging

config_logger()
logger = logging.getLogger(__name__)

LIMIT = 10


def _procs() -> list[dict]:
    procs = []
    for p in psutil.process_iter(["pid", "name", "username"]):
        try:
            cpu = p.cpu_percent(interval=0.0)
            with p.oneshot():
                rss = p.memory_info().rss
                name = p.info.get("name") or "?"
                user = p.info.get("username") or "?"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        procs.append({
            "pid": p.pid,
            "name": name,
            "user": user,
            "cpu_pct": round(cpu, 1),
            "rss_mb": round(rss / (1024 * 1024), 1),
        })
    return procs


def collect() -> dict:
    procs = _procs()
    by_cpu = sorted(procs, key=lambda p: p["cpu_pct"], reverse=True)[:LIMIT]
    by_mem = sorted(procs, key=lambda p: p["rss_mb"], reverse=True)[:LIMIT]
    return {"by_cpu": by_cpu, "by_mem": by_mem}
