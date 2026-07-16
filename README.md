---
runme:
  id: 01HJQ7F9RYFAQG4NCAYG2PW00T
  version: v3
---

# aia-device (nara-monitor)

Monitor en tiempo real del host `nara` (MSI H81M-E33, i3-4150, 8 GB RAM,
RTX 3060 12 GB, SSD 240 GB). Dashboard web ligero en Flask con refresh ~1.5 s.

## Métricas
- **CPU**: % uso, load 1/5/15, 2c/4t, temp (lm-sensors → coretemp Package id 0)
- **GPU**: % uso, VRAM usada/total, watts, temp, límite (nvidia-smi)
- **Total Watts**: CPU (RAPL) + GPU (nvidia-smi power.draw)
- **RAM**: usado/total 8 GB, %, temp DIMM (N/A si no hay sensor)
- **Disco**: uso `/`, I/O MB/s, temp SMART (smartctl)
- **Red**: RX/TX por interfaz (enp2s0, wlx0013eff21155, internet por default route)
- **Temperaturas**: CPU/GPU/RAM(N/A)/disco

## Desarrollo local
```sh
poetry install
poetry run daemon
# abrir http://localhost:9006
```

## Docker (en nara, x86_64)
```sh
# build
docker build . --platform linux/amd64 -t keitarodxs/aia_device:dev

# run (runtime nvidia + sensores del host)
docker run -d --name nara-monitor --restart=always \
  --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all \
  -p 9006:9006 \
  -v /run/nvidia:/run/nvidia:ro \
  -v /sys:/sys:ro \
  --pid host \
  keitarodxs/aia_device:dev
```
Desde el Mac: `http://nara:9006`

## CI / Release
- `docker-image.yml` construye en PR (tag = rama), en push a `main`
  (tag = `poetry version --short`) y en tags `v*.*.*`. Plataforma `linux/amd64`.
- El trigger de PR es temporal: se saca cuando el monitor funcione en nara.

