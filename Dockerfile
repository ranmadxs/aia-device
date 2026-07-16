# ─────────────────────────────────────────────────────────────────────────────
# aia-device (nara-monitor) — Dockerfile
#
# Imagen basada en keitarodxs/aia-utils-base (python:3.13-slim + poetry).
# nara es x86_64 (Intel i3-4150), por eso el build es linux/amd64.
# El runtime nvidia se registra en el host para exponer nvidia-smi a la GPU.
# ─────────────────────────────────────────────────────────────────────────────

FROM keitarodxs/aia-utils-base:1.0.0

WORKDIR /app

# ── Dependencias Python (capa cacheable) ─────────────────────────────────────
# Se copia SOLO pyproject.toml + poetry.lock ANTES del código fuente, así la
# capa de dependencias solo se reconstruye si cambian las deps, no el código.
# Se exporta a requirements.txt (respeta poetry.lock) y se instala con `uv pip
# install --system`, que es 10-100x más rápido que `pip install`.
# (Patrón tomado de aia-mcp.)
COPY pyproject.toml poetry.lock ./
# Poetry 1.8.x no incluye `export` por defecto: instala el plugin con el mismo
# pip que instaló poetry, para que lo detecte en el mismo entorno.
RUN pip install --no-cache-dir poetry-plugin-export \
    && poetry export -f requirements.txt --without-hashes -o /tmp/requirements.txt \
    && uv pip install --system -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# ── Código fuente (capa NO cacheable, va DESPUÉS de las deps) ───────
COPY . .
# Instala el paquete propio (registra el entry point `daemon`).
# Se usa pip (no uv) para consistencia con la imagen base y evitar fallos
# silenciosos de build que dejaran el entry point ausente.
RUN pip install --no-cache-dir .

# El dashboard escucha en 9006 dentro del contenedor.
EXPOSE 9006

CMD ["daemon"]
