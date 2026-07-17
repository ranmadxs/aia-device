import time

from aia_device.monitor import Monitor
from aia_device.web.app import create_app


def _snapshot(ts, gpu_vram):
    return {
        "timestamp": ts,
        "cpu": {"usage_percent": 10.0, "load": {"1": 1.0, "5": 1.0, "15": 1.0}, "temp_c": 40.0, "cores": 2, "threads": 4},
        "gpu": {"usage_percent": 20.0, "mem_used_mb": gpu_vram, "mem_total_mb": 12000, "power_w": 12.0, "temp_c": 45.0},
        "ram": {"usage_percent": 30.0, "used_gb": 2.0, "total_gb": 8.0, "temp_c": None},
        "disk": {"used_gb": 40.0, "total_gb": 100.0, "usage_percent": 40.0, "read_mbps": 0.0, "write_mbps": 0.0, "temp_c": None},
        "net": {"default_iface": "eth0", "interfaces": {}},
        "power": {"cpu_w": 5.0, "gpu_w": 12.0, "total_w": 17.0},
        "temps": {"cpu_c": 40.0, "gpu_c": 45.0, "ram_c": None, "disk_c": None},
    }


def test_history_1h_keeps_only_recent_entries(tmp_path, monkeypatch):
    monkeypatch.setenv("AIA_HISTORY_DIR", str(tmp_path))
    monitor = Monitor()

    old_entry = {"t": time.time() - 3700, "gpu_vram": 100}
    recent_entry = {"t": time.time() - 30, "gpu_vram": 200}
    monitor._persist_history_entry(old_entry)
    monitor._persist_history_entry(recent_entry)

    history = monitor.history("1h")

    assert len(history) == 1
    assert history[0]["gpu_vram"] == 200


def test_history_endpoint_supports_daily_range(tmp_path, monkeypatch):
    monkeypatch.setenv("AIA_HISTORY_DIR", str(tmp_path))
    monitor = Monitor()
    old_entry = {"t": time.time() - 2 * 60 * 60, "gpu_vram": 300}
    recent_entry = {"t": time.time() - 30 * 60, "gpu_vram": 400}
    monitor._persist_history_entry(old_entry)
    monitor._persist_history_entry(recent_entry)

    app = create_app()
    client = app.test_client()

    response = client.get("/api/history?range=1d")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert [item["gpu_vram"] for item in data] == [300, 400]
