// nara-monitor dashboard: estilo BIOS/UEFI + gráficos históricos en canvas.
const fmt = (v, unit = "") =>
  (v === null || v === undefined) ? '<span class="na">N/A</span>' : `${v}${unit}`;
const row = (k, v) => `<tr><td class="k">${k}</td><td class="v">${v}</td></tr>`;
const pct = (v) => Math.max(0, Math.min(100, v || 0));

// ── Gráfico de líneas genérico en canvas ────────────────────────────────────
function drawChart(canvas, series, opts = {}) {
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth, h = canvas.clientHeight;
  canvas.width = w * dpr; canvas.height = h * dpr;
  const ctx = canvas.getContext("2d");
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, w, h);

  // grid
  ctx.strokeStyle = "rgba(54,224,255,0.08)";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = (h / 4) * i + 0.5;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }

  const max = opts.max || Math.max(1, ...series.flatMap(s => s.data).filter(v => v != null)) * 1.15;
  const n = Math.max(...series.map(s => s.data.length), 2);
  const xAt = (i) => (n <= 1 ? w : (i / (n - 1)) * w);
  const yAt = (v) => h - (v / max) * h;

  for (const s of series) {
    ctx.strokeStyle = s.color;
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    let started = false;
    s.data.forEach((v, i) => {
      if (v == null) return;
      const x = xAt(i), y = yAt(v);
      if (!started) { ctx.moveTo(x, y); started = true; }
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    // glow final
    ctx.shadowColor = s.color; ctx.shadowBlur = 6;
    ctx.stroke(); ctx.shadowBlur = 0;
  }

  // etiqueta de escala
  ctx.fillStyle = "rgba(95,116,136,0.9)";
  ctx.font = "10px monospace";
  ctx.fillText(String(Math.round(max)) + (opts.unit || ""), 4, 12);
}

// ── Render de paneles (estado actual) ───────────────────────────────────────
function renderLive(m) {
  const p = m.power || {};
  document.getElementById("pw-total").innerHTML =
    `${fmt(p.total_w, "")}<span class="u">W</span>`;
  document.getElementById("pw-break").textContent =
    `CPU ${fmt(p.cpu_w, " W")} · GPU ${fmt(p.gpu_w, " W")}`;

  const c = m.cpu || {};
  document.getElementById("cpu-meta").textContent = `${c.cores || 0}c/${c.threads || 0}t`;
  document.getElementById("cpu-usage").innerHTML = `${fmt(c.usage_percent, "")}<span class="u">%</span>`;
  document.getElementById("cpu-bar").style.width = pct(c.usage_percent) + "%";
  document.getElementById("cpu-sub").textContent =
    `load ${fmt(c.load ? c.load["1"] : null)}/${fmt(c.load ? c.load["5"] : null)}/${fmt(c.load ? c.load["15"] : null)} · temp ${fmt(c.temp_c, "°C")}`;

  const g = m.gpu || {};
  document.getElementById("gpu-usage").innerHTML = `${fmt(g.usage_percent, "")}<span class="u">%</span>`;
  document.getElementById("gpu-bar").style.width = pct(g.usage_percent) + "%";
  document.getElementById("gpu-sub").textContent =
    `VRAM ${fmt(g.mem_used_mb, " MB")}/${fmt(g.mem_total_mb, " MB")} · ${fmt(g.power_w, " W")} · ${fmt(g.temp_c, "°C")}`;

  const r = m.ram || {};
  document.getElementById("ram-meta").textContent = `${fmt(r.total_gb, " GB")}`;
  document.getElementById("ram-usage").innerHTML = `${fmt(r.usage_percent, "")}<span class="u">%</span>`;
  document.getElementById("ram-bar").style.width = pct(r.usage_percent) + "%";
  document.getElementById("ram-sub").textContent = `${fmt(r.used_gb, " GB")} / ${fmt(r.total_gb, " GB")} GB`;

  // temperaturas
  const t = m.temps || {};
  document.getElementById("tbl-temps").innerHTML =
    row("CPU (Package)", fmt(t.cpu_c, " °C")) +
    row("GPU (RTX 3060)", fmt(t.gpu_c, " °C")) +
    row("RAM (DIMM)", fmt(t.ram_c, " °C")) +
    row("Disco (SMART)", fmt(t.disk_c, " °C"));

  // disco
  const d = m.disk || {};
  document.getElementById("tbl-disk").innerHTML =
    row("Uso", `${fmt(d.used_gb, " GB")} / ${fmt(d.total_gb, " GB")} (${fmt(d.usage_percent, " %")})`) +
    row("Lectura", fmt(d.read_mbps, " MB/s")) +
    row("Escritura", fmt(d.write_mbps, " MB/s")) +
    row("Temp", fmt(d.temp_c, " °C"));

  // red
  const net = m.net || {};
  document.getElementById("net-default").textContent = net.default_iface || "--";
  let nh = `<tr><td class="k">iface</td><td class="v">RX</td><td class="v">TX</td></tr>`;
  for (const [name, v] of Object.entries(net.interfaces || {})) {
    const tag = v.is_default ? " ◀ internet" : "";
    nh += `<tr><td class="k">${name}${tag}</td><td class="v">${fmt(v.rx_kbps, " KB/s")}</td><td class="v">${fmt(v.tx_kbps, " KB/s")}</td></tr>`;
  }
  document.getElementById("tbl-net").innerHTML = nh;
}

// ── Render de gráficos históricos ───────────────────────────────────────────
function renderHistory(hist) {
  const cpuW = hist.map(p => p.cpu_w);
  const gpuW = hist.map(p => p.gpu_w);
  const totW = hist.map(p => p.total_w);
  drawChart(document.getElementById("chart-power"),
    [{ color: "#36e0ff", data: cpuW }, { color: "#ffb000", data: gpuW }, { color: "#3fe07a", data: totW }],
    { unit: "W", max: 250 });

  const cpuU = hist.map(p => p.cpu_usage);
  const gpuU = hist.map(p => p.gpu_usage);
  drawChart(document.getElementById("chart-usage"),
    [{ color: "#36e0ff", data: cpuU }, { color: "#ffb000", data: gpuU }],
    { unit: "%", max: 100 });

  const ramU = hist.map(p => p.ram_usage);
  drawChart(document.getElementById("chart-ram"),
    [{ color: "#3fe07a", data: ramU }],
    { unit: "%", max: 100 });
}

// ── Loop ────────────────────────────────────────────────────────────────────
function clock() {
  document.getElementById("clock").textContent = new Date().toLocaleTimeString();
}

async function tick() {
  try {
    const [mr, hr] = await Promise.all([fetch("/api/metrics"), fetch("/api/history")]);
    const m = await mr.json();
    const h = await hr.json();
    renderLive(m);
    renderHistory(h);
  } catch (e) {
    console.error(e);
  }
}

clock();
tick();
setInterval(tick, 1500);
setInterval(clock, 1000);
