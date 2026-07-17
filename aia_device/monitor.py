"""Orquestador de métricas: cachea el snapshot cada ~1-2 s bajo demanda."""
import json
import logging
import os
import tempfile
import threading
import time
from pathlib import Path

from aia_utils.logs_cfg import config_logger

from aia_device.collectors import cpu, gpu, ram, disk, net, power, temps

config_logger()
logger = logging.getLogger(__name__)

_REFRESH_S = 1.5
_HISTORY_MAX = 2400  # ~1h a 1.5s de muestreo
_HISTORY_WINDOW_1H = 60 * 60
_HISTORY_WINDOW_1D = 24 * 60 * 60
_HISTORY_DIR = Path(os.getenv("AIA_HISTORY_DIR", "/data/history"))


def _resolve_history_dir() -> Path:
    """Devuelve un directorio escribible para la historia persistida."""
    configured = Path(os.getenv("AIA_HISTORY_DIR", "/data/history"))
    if configured.exists() and not configured.is_dir():
        return Path(tempfile.gettempdir()) / "aia-history"
    try:
        configured.mkdir(parents=True, exist_ok=True)
        return configured
    except OSError:
        fallback = Path(tempfile.gettempdir()) / "aia-history"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


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
        "gpu_vram": (snap.get("gpu") or {}).get("mem_used_mb"),
        "cpu_temp": (snap.get("temps") or {}).get("cpu_c"),
        "gpu_temp": (snap.get("temps") or {}).get("gpu_c"),
    }


class Monitor:
    def __init__(self):
        self._lock = threading.RLock()
        self._snapshot = None
        self._ts = 0.0
        self._history = []
        self._history_dir = _resolve_history_dir()
        self._history_dir.mkdir(parents=True, exist_ok=True)
        self._load_persisted_history()

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

    def _history_file_for(self, ts: float | None = None) -> Path:
        stamp = ts if ts is not None else time.time()
        date = time.strftime("%Y-%m-%d", time.localtime(stamp))
        return self._history_dir / f"{date}.json"

    def _load_persisted_history(self) -> list[dict]:
        entries: list[dict] = []
        for history_file in sorted(self._history_dir.glob("*.json")):
            try:
                with history_file.open("r", encoding="utf-8") as handle:
                    payload = json.load(handle)
                if isinstance(payload, list):
                    entries.extend(payload)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("no se pudo cargar %s: %s", history_file, exc)
        if entries:
            entries = sorted(entries, key=lambda item: item.get("t") or 0)
            self._history = entries[-_HISTORY_MAX:]
        else:
            self._history = []
        return list(self._history)

    def _read_persisted_entries(self) -> list[dict]:
        entries: list[dict] = []
        for history_file in sorted(self._history_dir.glob("*.json")):
            try:
                with history_file.open("r", encoding="utf-8") as handle:
                    payload = json.load(handle)
                if isinstance(payload, list):
                    entries.extend(payload)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("no se pudo leer %s: %s", history_file, exc)
        return sorted(entries, key=lambda item: item.get("t") or 0)

    def _persist_history_entry(self, entry: dict) -> None:
        history_file = self._history_file_for(entry.get("t"))
        history_file.parent.mkdir(parents=True, exist_ok=True)
        payload: list[dict] = []
        if history_file.exists():
            try:
                with history_file.open("r", encoding="utf-8") as handle:
                    existing = json.load(handle)
                if isinstance(existing, list):
                    payload = existing
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("no se pudo cargar %s para persistir: %s", history_file, exc)
        payload.append(entry)
        with history_file.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle)

        with self._lock:
            self._history.append(entry)
            if len(self._history) > _HISTORY_MAX:
                self._history.pop(0)

    def snapshot(self) -> dict:
        now = time.time()
        with self._lock:
            if self._snapshot is None or (now - self._ts) >= _REFRESH_S:
                try:
                    self._snapshot = self._build()
                    self._ts = now
                    self._persist_history_entry(_extract_series(self._snapshot))
                except Exception as e:  # nunca romper el dashboard
                    logger.error(f"error recolectando métricas: {e}")
                    if self._snapshot is None:
                        self._snapshot = {"error": str(e)}
        return self._snapshot

    def history(self, range: str = "1h") -> list:
        now = time.time()
        window = _HISTORY_WINDOW_1H if range != "1d" else _HISTORY_WINDOW_1D
        with self._lock:
            combined = list(self._history) + self._read_persisted_entries()
        deduped: dict[float, dict] = {}
        for item in combined:
            ts = item.get("t")
            if ts is None:
                continue
            if now - ts <= window:
                deduped[ts] = item
        return sorted(deduped.values(), key=lambda item: item.get("t") or 0)

    def history_dates(self) -> list[str]:
        return sorted(path.stem for path in self._history_dir.glob("*.json"))


monitor = Monitor()
