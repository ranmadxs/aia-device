---
runme:
  id: 01HJQ7JXMD6NADWWC23SR9W42S
  version: v3
---

# RELEASE

## [1.0.4] - 2026-07-16
### Fixed
- 🐛 Red: el contenedor no veía las interfaces de nara. `deploy-nara` ahora usa
  `--network host` (en vez de solo `--pid host`) y `net.py` lee la ruta por
  defecto desde `/proc/net/route` (sin depender de `ip`).
- 🐛 CPU temp: instala `lm-sensors` en el Dockerfile (no venía en la base
  python:3.13-slim) para que `sensors` exponga `Package id 0`.

## [1.0.3] - 2026-07-15
### Changed
- ♻️ Workflow `docker-image.yml`: misma estructura de 3 jobs que aia-mcp
  (`build` → `publish` → `deploy-nara`). `deploy-nara` corre en el runner
  self-hosted `[self-hosted, nara]` (pull + docker run con runtime nvidia,
  sensores y --device /dev/sda). Mantiene versiones PR/main/tag.

## [1.0.2] - 2026-07-15
### Fixed
- 🐛 Alinea `python` a `^3.13` para coincidir con la imagen base
  `keitarodxs/aia-utils-base:v1.0.0` (python:3.13-slim). La restricción
  anterior `<3.12` era incompatible con la base y rompía `poetry export`/`uv`.

## [1.0.1] - 2026-07-15
### Fixed
- 🐛 Corrige tag de imagen base: `keitarodxs/aia-utils-base:1.0.0` → `v1.0.0`
  (el tag sin `v` no existe en Docker Hub; buildx fallaba con `not found`).

## [1.0.0] - 2026-07-15
### ⚠️ BREAKING CHANGE (refactor total → nara-monitor)
- `aia-device` deja de ser el servicio de pantalla ILI9486/Kafka y se convierte
  en un monitor en tiempo real del host `nara`.
- **Borrado**: `driver/` (ILI9486), `transform.py`, `deviceSvc.py`, `resources/images`.
- **Nuevo**: `collectors/` (cpu, gpu, power, ram, disk, net, temps), `monitor.py`
  (orquestador con cache ~1.5 s) y `web/` (Flask: `/` dashboard + `/api/metrics`).
- **Dependencias**: se cambia Pillow/numpy/scipy/scikit-image/pymongo por
  `Flask` + `psutil` (poetry se mantiene como package manager).
- **Dockerfile**: base `keitarodxs/aia-utils-base:1.0.0`, instalación de deps con
  `poetry export` + `uv pip install --system` (patrón aia-mcp), build `linux/amd64`.
- **Workflow** `docker-image.yml`: triggers `pull_request` / `push main` / `tag v*.*.*`,
  multi-plataforma `linux/amd64`, release en merge a main. El trigger de PR es
  temporal (se saca cuando funcione en nara).
- Métricas: CPU %, load, cores/threads, temp; GPU %/VRAM/watts/temp/límite;
  Total Watts (RAPL+GPU); RAM; disco uso/I/O/temp; red RX/TX por interfaz;
  temperaturas agregadas.

[0.2.13] 13-ago-2024
- 🔄 Update aia-utils=0.3.3

[0.2.10] 08-ago-2024

- ✨ Feature: text2img
- ✨ Add ip to image
- 🐛🔧 BugFix get Default Font

[0.1.0] 29-ene-2024

- ✨ Feature: Stream images

[0.0.5] 22-ene-2024

- 🐛🔧 Fix Rotate Img 90ª

[0.0.4] 21-ene-2024

- ✨ Feature: Read images from Kafka Queue.

[0.0.3] 15-ene-2024

- 🔥🔧 Hotfix: Add Try Catch send to device.
- ✨ Add error.png

[0.0.2] First Version 05-ene-2024

- ✨ Feature: Add Device Driver ILI9486
- ✨ Kafka support

```