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

  const padBottom = opts.padBottom || 0;
  const plotH = h - padBottom;

  // grid
  ctx.strokeStyle = "rgba(54,224,255,0.08)";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = (plotH / 4) * i + 0.5;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }

  const max = opts.max || Math.max(1, ...series.flatMap(s => s.data).filter(v => v != null)) * 1.15;
  const n = Math.max(...series.map(s => s.data.length), 2);
  const xAt = (i) => (n <= 1 ? w : (i / (n - 1)) * w);
  const yAt = (v) => plotH - (v / max) * plotH;

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

  // etiquetas de hora a lo largo del eje (inicio / medio / fin)
  if (opts.times && opts.times.length) {
    const idxs = [0, Math.floor((n - 1) / 2), n - 1].filter((v, i, a) => a.indexOf(v) === i);
    idxs.forEach(i => {
      const ts = opts.times[i];
      if (ts == null) return;
      const label = new Date(ts * 1000).toLocaleTimeString();
      const x = xAt(i);
      ctx.textAlign = i === 0 ? "left" : (i === n - 1 ? "right" : "center");
      ctx.fillText(label, Math.max(2, Math.min(w - 2, x)), h - 3);
    });
    ctx.textAlign = "left";
  }
}

// ── Batería de watts (tope 500W, zonas de color) ───────────────────────────
function drawBattery(watts) {
  const canvas = document.getElementById("battery");
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth || 120, h = canvas.clientHeight || 56;
  canvas.width = w * dpr; canvas.height = h * dpr;
  const ctx = canvas.getContext("2d");
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, w, h);

  const MAX = 500;
  const bx = 4, by = 8, bw = w - 22, bh = h - 16;
  const lvl = Math.max(0, Math.min(MAX, watts || 0)) / MAX;

  // color por zona
  let color = "#36e0ff"; // azul < 200
  if (watts >= 400) color = "#ff5a5a";       // rojo 400-500
  else if (watts >= 200) color = "#ffb000";  // naranja 200-400

  // cuerpo
  ctx.strokeStyle = "rgba(54,224,255,0.5)";
  ctx.lineWidth = 2;
  ctx.strokeRect(bx, by, bw, bh);
  // terminal
  ctx.fillStyle = "rgba(54,224,255,0.5)";
  ctx.fillRect(bx + bw, by + bh / 2 - 6, 8, 12);

  // zonas de fondo
  const z = (a, b, c) => { ctx.fillStyle = c; ctx.fillRect(bx + 1, by + 1, (bw - 2) * (b / MAX), bh - 2); };
  z(0, 200, "rgba(54,224,255,0.06)");
  z(200, 400, "rgba(255,176,0,0.06)");
  z(400, 500, "rgba(255,90,90,0.08)");

  // nivel
  ctx.fillStyle = color;
  ctx.shadowColor = color; ctx.shadowBlur = 8;
  ctx.fillRect(bx + 1, by + 1, (bw - 2) * lvl, bh - 2);
  ctx.shadowBlur = 0;

  // texto
  ctx.fillStyle = color;
  ctx.font = "bold 13px monospace";
  ctx.textAlign = "center";
  ctx.fillText(`${Math.round(watts || 0)}W`, bx + bw / 2, by + bh / 2 + 4);
  ctx.textAlign = "left";
}

// ── Render de paneles (estado actual) ───────────────────────────────────────
function renderLive(m) {
  const p = m.power || {};
  document.getElementById("pw-total").innerHTML =
    `${fmt(p.total_w, "")}<span class="u">W</span>`;
  document.getElementById("pw-break").textContent =
    `CPU ${fmt(p.cpu_w, " W")} · GPU ${fmt(p.gpu_w, " W")}`;
  drawBattery(p.total_w);

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

  // vram (live, estilo RAM)
  const gv = m.gpu || {};
  const vTotal = gv.mem_total_mb || 0;
  const vUsed = gv.mem_used_mb || 0;
  const vPct = vTotal ? (vUsed / vTotal) * 100 : 0;
  document.getElementById("vram-meta").textContent = `${fmt(vTotal, " MB")}`;
  document.getElementById("vram-usage").innerHTML = `${fmt(Math.round(vPct), "")}<span class="u">%</span>`;
  document.getElementById("vram-bar").style.width = pct(vPct) + "%";
  document.getElementById("vram-sub").textContent = `${fmt(vUsed, " MB")} / ${fmt(vTotal, " MB")} MB`;

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
  const times = hist.map(p => p.t);
  const dateStr = times.length
    ? new Date(times[times.length - 1] * 1000).toLocaleDateString()
    : "--";

  const cpuW = hist.map(p => p.cpu_w);
  const gpuW = hist.map(p => p.gpu_w);
  const totW = hist.map(p => p.total_w);
  drawChart(document.getElementById("chart-power"),
    [{ color: "#36e0ff", data: cpuW }, { color: "#ffb000", data: gpuW }, { color: "#3fe07a", data: totW }],
    { unit: "W", max: 250, times, padBottom: 14 });
  document.getElementById("power-date").textContent = dateStr;

  const cpuU = hist.map(p => p.cpu_usage);
  const gpuU = hist.map(p => p.gpu_usage);
  drawChart(document.getElementById("chart-usage"),
    [{ color: "#36e0ff", data: cpuU }, { color: "#ffb000", data: gpuU }],
    { unit: "%", max: 100, times, padBottom: 14 });
  document.getElementById("usage-date").textContent = dateStr;

  const ramU = hist.map(p => p.ram_usage);
  drawChart(document.getElementById("chart-ram"),
    [{ color: "#3fe07a", data: ramU }],
    { unit: "%", max: 100, times, padBottom: 14 });
  document.getElementById("ram-date").textContent = dateStr;

  // historial VRAM con marcas de hora
  const vram = hist.map(p => p.gpu_vram);
  drawChart(document.getElementById("chart-vram"),
    [{ color: "#ffb000", data: vram }],
    { unit: "MB", times, padBottom: 14 });
  document.getElementById("vram-date").textContent = dateStr;
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
