"""Temps collector: agrega CPU/GPU/RAM(N/A)/disco en una sola vista."""


def collect(cpu: dict, gpu: dict, ram: dict, disk: dict) -> dict:
    return {
        "cpu_c": cpu.get("temp_c"),
        "gpu_c": gpu.get("temp_c") if gpu.get("available") else None,
        "ram_c": ram.get("temp_c"),  # None => N/A
        "disk_c": disk.get("temp_c"),
    }
