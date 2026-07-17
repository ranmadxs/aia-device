// nara-monitor dashboard: estilo MSI Click BIOS 5.
// Menú lateral de íconos + panel central por categoría.
const fmt = (v, unit = "") =>
  (v === null || v === undefined) ? '<span class="na">N/A</span>' : `${v}${unit}`;
const row = (k, v) => `<tr><td class="k">${k}</td><td class="v">${v}</td></tr>`;
const pct = (v) => Math.max(0, Math.min(100, v || 0));
const brandBlock = (d) => {
  const b = d?.brand, m = d?.model;
  if (!b && !m) return "";
  return `<div class="brandline"><span class="b">${b || "—"}</span>` +
    (m ? `<span class="m">${m}</span>` : "") + `</div>`;
};
const topTable = (top, kind) => {
  const rows = (top?.[kind] || []);
  if (!rows.length) return '<div class="sub">sin datos</div>';
  let h = '<table><tr><td class="k">PID</td><td class="k">Proc</td><td class="k">User</td>' +
    (kind === "by_cpu" ? '<td class="v">CPU%</td>' : '<td class="v">RAM MB</td>') + '</tr>';
  for (const p of rows) {
    h += `<tr><td class="k">${p.pid}</td><td class="k">${p.name}</td><td class="k">${p.user}</td>` +
      `<td class="v">${kind === "by_cpu" ? fmt(p.cpu_pct, " %") : fmt(p.rss_mb)}</td></tr>`;
  }
  return h + '</table>';
};
const topCard = (top) => `
  <div class="card col-6">
    <h3>TOP 10 · CPU</h3>
    ${topTable(top, "by_cpu")}
  </div>
  <div class="card col-6">
    <h3>TOP 10 · RAM</h3>
    ${topTable(top, "by_mem")}
  </div>`;
const ICONS = {
  system: '<svg class="ic" viewBox="0 0 24 24"><path d="M3 3h8v8H3V3zm10 0h8v8h-8V3zM3 13h8v8H3v-8zm10 0h8v8h-8v-8z"/></svg>',
  cpu: '<svg class="ic" viewBox="0 0 24 24"><path d="M7 7h10v10H7V7zm-3 3H2v4h2v-4zm16 0h-2v4h2v-4zM9 2v2h6V2H9zm0 20v-2h6v2H9z"/></svg>',
  gpu: '<svg class="ic" viewBox="0 0 24 24"><path d="M3 5h18v11H13l4 3v2h-2l-2-3H8l-2 3H4v-2l4-3H3V5zm3 3v6h12V8H6z"/></svg>',
  ram: '<svg class="ic" viewBox="0 0 24 24"><path d="M2 7h20v4H2V7zm0 6h20v4H2v-4zM5 4v3h2V4H5zm4 0v3h2V4H9zm4 0v3h2V4h-2zm4 0v3h2V4h-2z"/></svg>',
  vram: '<svg class="ic" viewBox="0 0 24 24"><path d="M3 5h18v11H13l4 3v2h-2l-2-3H8l-2 3H4v-2l4-3H3V5zm3 3v6h12V8H6z"/></svg>',
  watts: '<svg class="ic" viewBox="0 0 24 24"><path d="M13 2L4 14h6l-1 8 9-12h-6l1-8z"/></svg>',
  disk: '<svg class="ic" viewBox="0 0 24 24"><path d="M4 4h16v16H4V4zm2 2v5h12V6H6zm0 8v4h5v-4H6zm7 0v4h5v-4h-5z"/></svg>',
  net: '<svg class="ic" viewBox="0 0 24 24"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 3a7 7 0 015.2 2.3L12 12 6.8 7.3A7 7 0 0112 5zm-7 7a7 7 0 014.3-5.2L12 12l-4.9 5.2A7 7 0 015 12zm14 0a7 7 0 01-4.3 5.2L12 12l4.9-5.2A7 7 0 0119 12z"/></svg>',
};

let currentView = "system";
let lastMetrics = null;
let lastHistory = [];

function drawChart(canvas, series, opts = {}) {
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth, h = canvas.clientHeight;
  canvas.width = w * dpr; canvas.height = h * dpr;
  const ctx = canvas.getContext("2d");
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, w, h);
  const padBottom = opts.padBottom || 0;
  const plotH = h - padBottom;
  ctx.strokeStyle = "rgba(47,212,255,0.08)";
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
    ctx.shadowColor = s.color; ctx.shadowBlur = 6;
    ctx.stroke(); ctx.shadowBlur = 0;
  }
  ctx.fillStyle = "rgba(93,114,134,0.9)";
  ctx.font = "10px monospace";
  ctx.fillText(String(Math.round(max)) + (opts.unit || ""), 4, 12);
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

function battery(watts) {
  const el = document.getElementById("bat-canvas");
  if (!el) return;
  const dpr = window.devicePixelRatio || 1;
  const w = el.clientWidth || 120, h = el.clientHeight || 56;
  el.width = w * dpr; el.height = h * dpr;
  const ctx = el.getContext("2d");
  ctx.scale(dpr, dpr); ctx.clearRect(0, 0, w, h);
  const MAX = 500, bx = 4, by = 8, bw = w - 22, bh = h - 16;
  const lvl = Math.max(0, Math.min(MAX, watts || 0)) / MAX;
  let color = "#2fd4ff";
  if (watts >= 400) color = "#ff1f3d";
  else if (watts >= 200) color = "#ffb000";
  ctx.strokeStyle = "rgba(47,212,255,0.5)"; ctx.lineWidth = 2;
  ctx.strokeRect(bx, by, bw, bh);
  ctx.fillStyle = "rgba(47,212,255,0.5)";
  ctx.fillRect(bx + bw, by + bh / 2 - 6, 8, 12);
  const z = (a, b, c) => { ctx.fillStyle = c; ctx.fillRect(bx + 1, by + 1, (bw - 2) * (b / MAX), bh - 2); };
  z(0, 200, "rgba(47,212,255,0.06)");
  z(200, 400, "rgba(255,176,0,0.06)");
  z(400, 500, "rgba(255,31,61,0.08)");
  ctx.fillStyle = color; ctx.shadowColor = color; ctx.shadowBlur = 8;
  ctx.fillRect(bx + 1, by + 1, (bw - 2) * lvl, bh - 2);
  ctx.shadowBlur = 0;
  ctx.fillStyle = color; ctx.font = "bold 13px monospace"; ctx.textAlign = "center";
  ctx.fillText(`${Math.round(watts || 0)}W`, bx + bw / 2, by + bh / 2 + 4);
  ctx.textAlign = "left";
}

// ── Vistas ────────────────────────────────────────────────────────────
function viewSystem(m, hist) {
  const p = m.power || {}, c = m.cpu || {}, g = m.gpu || {};
  const date = hist.length
    ? new Date(hist[hist.length - 1].t * 1000).toLocaleDateString() : "--";
  return `
    <div class="view-title">${ICONS.system} SYSTEM MONITOR</div>
    <div class="brandline"><span class="b">NARA</span><span class="m">host · ${fmt(c.brand)} ${fmt(c.model)}</span></div>
    <div class="cards">
      <div class="card col-3">
        <h3>TOTAL WATTS</h3>
        <div class="big">${fmt(p.total_w)}<span class="u">W</span></div>
        <div class="sub">CPU ${fmt(p.cpu_w," W")} · GPU ${fmt(p.gpu_w," W")}</div>
        <div style="margin-top:10px"><canvas id="bat-canvas" width="120" height="56"></canvas></div>
      </div>
      <div class="card col-3">
        <h3>CPU</h3>
        <div class="big">${fmt(c.usage_percent)}<span class="u">%</span></div>
        <div class="bar"><i style="width:${pct(c.usage_percent)}%"></i></div>
        <div class="sub">${fmt(c.cores)}c/${fmt(c.threads)}t · ${fmt(c.temp_c,"°C")}</div>
      </div>
      <div class="card col-3">
        <h3>GPU</h3>
        <div class="big">${fmt(g.usage_percent)}<span class="u">%</span></div>
        <div class="bar"><i style="width:${pct(g.usage_percent)}%"></i></div>
        <div class="sub">${fmt(g.brand)} ${fmt(g.model)}</div>
      </div>
      <div class="card col-3">
        <h3>RAM</h3>
        <div class="big">${fmt(m.ram?.usage_percent)}<span class="u">%</span></div>
        <div class="bar"><i style="width:${pct(m.ram?.usage_percent)}%"></i></div>
        <div class="sub">${fmt(m.ram?.used_gb," GB")} / ${fmt(m.ram?.total_gb," GB")}</div>
      </div>
      <div class="card col-6">
        <h3>CONSUMO DE POTENCIA <span style="float:right;color:var(--txt-dim)">${date}</span></h3>
        <canvas id="ch-power"></canvas>
        <div class="legend"><span><i style="background:#2fd4ff"></i>CPU</span><span><i style="background:#ffb000"></i>GPU</span><span><i style="background:#36e07a"></i>Total</span></div>
      </div>
      <div class="card col-6">
        <h3>USO CPU / GPU <span style="float:right;color:var(--txt-dim)">${date}</span></h3>
        <canvas id="ch-usage"></canvas>
        <div class="legend"><span><i style="background:#2fd4ff"></i>CPU</span><span><i style="background:#ffb000"></i>GPU</span></div>
      </div>
    </div>`;
}

function viewCpu(c, hist) {
  const date = hist.length ? new Date(hist[hist.length - 1].t * 1000).toLocaleDateString() : "--";
  return `
    <div class="view-title">${ICONS.cpu} CPU</div>
    ${brandBlock(c)}
    <div class="cards">
      <div class="card col-4">
        <h3>USO</h3>
        <div class="big">${fmt(c.usage_percent)}<span class="u">%</span></div>
        <div class="bar"><i style="width:${pct(c.usage_percent)}%"></i></div>
        <div class="sub">load ${fmt(c.load?.["1"])}/${fmt(c.load?.["5"])}/${fmt(c.load?.["15"])}</div>
      </div>
      <div class="card col-4">
        <h3>TEMPERATURA</h3>
        <div class="big">${fmt(c.temp_c)}<span class="u">°C</span></div>
        <div class="sub">núcleos ${fmt(c.cores)} · hilos ${fmt(c.threads)}</div>
      </div>
      <div class="card col-4">
        <h3>LOAD AVERAGE</h3>
        <table>
          <tr><td class="k">1 min</td><td class="v">${fmt(c.load?.["1"])}</td></tr>
          <tr><td class="k">5 min</td><td class="v">${fmt(c.load?.["5"])}</td></tr>
          <tr><td class="k">15 min</td><td class="v">${fmt(c.load?.["15"])}</td></tr>
        </table>
      </div>
      <div class="card col-12">
        <h3>USO HISTÓRICO <span style="float:right;color:var(--txt-dim)">${date}</span></h3>
        <canvas id="ch-usage"></canvas>
        <div class="legend"><span><i style="background:#2fd4ff"></i>CPU %</span></div>
      </div>
    </div>`;
}

function viewGpu(g, hist) {
  const date = hist.length ? new Date(hist[hist.length - 1].t * 1000).toLocaleDateString() : "--";
  return `
    <div class="view-title">${ICONS.gpu} GPU</div>
    ${brandBlock(g)}
    <div class="cards">
      <div class="card col-4">
        <h3>USO</h3>
        <div class="big">${fmt(g.usage_percent)}<span class="u">%</span></div>
        <div class="bar"><i style="width:${pct(g.usage_percent)}%"></i></div>
        <div class="sub">${fmt(g.power_w," W")} · límite ${fmt(g.power_limit_w," W")}</div>
      </div>
      <div class="card col-4">
        <h3>VRAM</h3>
        <div class="big">${fmt(g.mem_used_mb)}<span class="u">MB</span></div>
        <div class="bar"><i style="width:${pct(g.mem_total_mb ? g.mem_used_mb / g.mem_total_mb * 100 : 0)}%"></i></div>
        <div class="sub">${fmt(g.mem_used_mb)} / ${fmt(g.mem_total_mb)} MB</div>
      </div>
      <div class="card col-4">
        <h3>TEMP / POWER</h3>
        <div class="big">${fmt(g.temp_c)}<span class="u">°C</span></div>
        <div class="sub">${fmt(g.power_w," W")} draw</div>
      </div>
      <div class="card col-12">
        <h3>USO HISTÓRICO <span style="float:right;color:var(--txt-dim)">${date}</span></h3>
        <canvas id="ch-usage"></canvas>
        <div class="legend"><span><i style="background:#ffb000"></i>GPU %</span></div>
      </div>
    </div>`;
}

function viewRam(r, hist, sysTemp) {
  const date = hist.length ? new Date(hist[hist.length - 1].t * 1000).toLocaleDateString() : "--";
  const ramTemp = r.temp_c;
  const tempVal = ramTemp != null ? ramTemp : sysTemp;
  const tempNote = ramTemp != null ? "sensor DIMM" : "ref. sistema (sin sensor DIMM)";
  return `
    <div class="view-title">${ICONS.ram} RAM</div>
    ${brandBlock(r)}
    <div class="cards">
      <div class="card col-4">
        <h3>USO</h3>
        <div class="big">${fmt(r.usage_percent)}<span class="u">%</span></div>
        <div class="bar"><i style="width:${pct(r.usage_percent)}%"></i></div>
        <div class="sub">${fmt(r.used_gb," GB")} / ${fmt(r.total_gb," GB")}</div>
      </div>
      <div class="card col-4">
        <h3>TOTAL</h3>
        <div class="big">${fmt(r.total_gb)}<span class="u">GB</span></div>
        <div class="sub">usado ${fmt(r.used_gb," GB")}</div>
      </div>
      <div class="card col-4">
        <h3>TEMP</h3>
        <div class="big">${fmt(tempVal)}<span class="u">°C</span></div>
        <div class="sub">${tempNote}</div>
      </div>
      <div class="card col-12">
        <h3>USO HISTÓRICO <span style="float:right;color:var(--txt-dim)">${date}</span></h3>
        <canvas id="ch-ram"></canvas>
        <div class="legend"><span><i style="background:#36e07a"></i>RAM %</span></div>
      </div>
    </div>`;
}

function viewVram(g, hist) {
  const date = hist.length ? new Date(hist[hist.length - 1].t * 1000).toLocaleDateString() : "--";
  return `
    <div class="view-title">${ICONS.vram} VRAM</div>
    ${brandBlock(g)}
    <div class="cards">
      <div class="card col-6">
        <h3>USO</h3>
        <div class="big">${fmt(g.mem_used_mb)}<span class="u">MB</span></div>
        <div class="bar"><i style="width:${pct(g.mem_total_mb ? g.mem_used_mb / g.mem_total_mb * 100 : 0)}%"></i></div>
        <div class="sub">${fmt(g.mem_used_mb)} / ${fmt(g.mem_total_mb)} MB (${fmt(g.mem_total_mb ? Math.round(g.mem_used_mb / g.mem_total_mb * 100) : 0)}%)</div>
      </div>
      <div class="card col-6">
        <h3>GPU</h3>
        <div class="big">${fmt(g.brand)}</div>
        <div class="sub">${fmt(g.model)}</div>
      </div>
      <div class="card col-12">
        <h3>HISTÓRICO VRAM (MB) <span style="float:right;color:var(--txt-dim)">${date}</span></h3>
        <canvas id="ch-vram"></canvas>
        <div class="legend"><span><i style="background:#ffb000"></i>VRAM MB</span></div>
      </div>
    </div>`;
}

function viewWatts(p, hist) {
  const date = hist.length ? new Date(hist[hist.length - 1].t * 1000).toLocaleDateString() : "--";
  return `
    <div class="view-title">${ICONS.watts} WATTS</div>
    <div class="cards">
      <div class="card col-4">
        <h3>TOTAL</h3>
        <div class="big">${fmt(p.total_w)}<span class="u">W</span></div>
        <div style="margin-top:10px"><canvas id="bat-canvas" width="120" height="56"></canvas></div>
      </div>
      <div class="card col-4">
        <h3>CPU</h3>
        <div class="big">${fmt(p.cpu_w)}<span class="u">W</span></div>
      </div>
      <div class="card col-4">
        <h3>GPU</h3>
        <div class="big">${fmt(p.gpu_w)}<span class="u">W</span></div>
        <div class="sub">límite ${fmt(p.gpu_limit_w ?? p.gpu_limit_w," W")}</div>
      </div>
      <div class="card col-12">
        <h3>CONSUMO HISTÓRICO <span style="float:right;color:var(--txt-dim)">${date}</span></h3>
        <canvas id="ch-power"></canvas>
        <div class="legend"><span><i style="background:#2fd4ff"></i>CPU</span><span><i style="background:#ffb000"></i>GPU</span><span><i style="background:#36e07a"></i>Total</span></div>
      </div>
    </div>`;
}

function viewDisk(d, hist) {
  return `
    <div class="view-title">${ICONS.disk} DISCO</div>
    ${brandBlock(d)}
    <div class="cards">
      <div class="card col-4">
        <h3>USO</h3>
        <div class="big">${fmt(d.usage_percent)}<span class="u">%</span></div>
        <div class="bar"><i style="width:${pct(d.usage_percent)}%"></i></div>
        <div class="sub">${fmt(d.used_gb," GB")} / ${fmt(d.total_gb," GB")}</div>
      </div>
      <div class="card col-4">
        <h3>I/O</h3>
        <table>
          <tr><td class="k">Lectura</td><td class="v">${fmt(d.read_mbps," MB/s")}</td></tr>
          <tr><td class="k">Escritura</td><td class="v">${fmt(d.write_mbps," MB/s")}</td></tr>
          <tr><td class="k">Temp</td><td class="v">${fmt(d.temp_c," °C")}</td></tr>
        </table>
      </div>
      <div class="card col-4">
        <h3>MONTAJE</h3>
        <table>
          <tr><td class="k">Mount</td><td class="v">${fmt(d.mount)}</td></tr>
          <tr><td class="k">Device</td><td class="v">${fmt(d.device)}</td></tr>
        </table>
      </div>
    </div>`;
}

function viewNet(net, hist) {
  const def = net.default_iface || "--";
  let rows = `<tr><td class="k">iface</td><td class="v">RX</td><td class="v">TX</td></tr>`;
  for (const [name, v] of Object.entries(net.interfaces || {})) {
    const tag = v.is_default ? " ◀ internet" : "";
    rows += `<tr><td class="k">${name}${tag}</td><td class="v">${fmt(v.rx_kbps," KB/s")}</td><td class="v">${fmt(v.tx_kbps," KB/s")}</td></tr>`;
  }
  return `
    <div class="view-title">${ICONS.net} RED</div>
    ${brandBlock(net)}
    <div class="cards">
      <div class="card col-6">
        <h3>INTERFAZ PRINCIPAL</h3>
        <div class="big">${fmt(def)}</div>
        <div class="sub">${fmt(net.brand)} ${fmt(net.model)}</div>
      </div>
      <div class="card col-6">
        <h3>TRÁFICO</h3>
        <table>${rows}</table>
      </div>
      ${topCard(lastMetrics.top || {})}
    </div>`;
}

function renderView() {
  if (!lastMetrics) return;
  const m = lastMetrics;
  const root = document.getElementById("view-root");
  const crumb = document.getElementById("crumb");
  let html;
  switch (currentView) {
    case "cpu": html = viewCpu(m.cpu || {}, lastHistory); crumb.textContent = "CPU"; break;
    case "gpu": html = viewGpu(m.gpu || {}, lastHistory); crumb.textContent = "GPU"; break;
    case "ram": html = viewRam(m.ram || {}, lastHistory, (m.cpu||{}).temp_c); crumb.textContent = "RAM"; break;
    case "vram": html = viewVram(m.gpu || {}, lastHistory); crumb.textContent = "VRAM"; break;
    case "watts": html = viewWatts(m.power || {}, lastHistory); crumb.textContent = "Watts"; break;
    case "disk": html = viewDisk(m.disk || {}, lastHistory); crumb.textContent = "Disco"; break;
    case "net": html = viewNet(m.net || {}, lastHistory); crumb.textContent = "Red"; break;
    default: html = viewSystem(m, lastHistory); crumb.textContent = "System";
  }
  root.innerHTML = html;
  renderHistory(lastHistory);
  if (currentView === "system" || currentView === "watts") battery((m.power || {}).total_w);
}

function renderHistory(hist) {
  const times = hist.map(p => p.t);
  const mk = (id, series, opts) => {
    const el = document.getElementById(id);
    if (el) drawChart(el, series, { ...opts, times });
  };
  mk("ch-power", [
    { color: "#2fd4ff", data: hist.map(p => p.cpu_w) },
    { color: "#ffb000", data: hist.map(p => p.gpu_w) },
    { color: "#36e07a", data: hist.map(p => p.total_w) },
  ], { unit: "W", max: 250, padBottom: 14 });
  mk("ch-usage", [
    { color: "#2fd4ff", data: hist.map(p => p.cpu_usage) },
    { color: "#ffb000", data: hist.map(p => p.gpu_usage) },
  ], { unit: "%", max: 100, padBottom: 14 });
  mk("ch-ram", [{ color: "#36e07a", data: hist.map(p => p.ram_usage) }],
    { unit: "%", max: 100, padBottom: 14 });
  mk("ch-vram", [{ color: "#ffb000", data: hist.map(p => p.gpu_vram) }],
    { unit: "MB", padBottom: 14 });
}

function topbar(m) {
  const p = m.power || {}, c = m.cpu || {}, g = m.gpu || {};
  document.getElementById("tb-temp").textContent = `${fmt(c.temp_c ?? g.temp_c, "°C")}`;
  document.getElementById("tb-watts").textContent = `${fmt(p.total_w, " W")}`;
}

async function loadHistory(range = "1h") {
  try {
    const [hr, datesRes] = await Promise.all([
      fetch(`/api/history?range=${range}`),
      fetch("/api/history_dates"),
    ]);
    lastHistory = await hr.json();
    renderView();
    const select = document.getElementById("range-select");
    if (select) select.title = `Fechas: ${ (await datesRes.json()).join(", ") || "ninguna" }`;
  } catch (e) { console.error(e); }
}

async function tick() {
  try {
    const m = await (await fetch("/api/metrics")).json();
    lastMetrics = m;
    topbar(m);
    renderView();
    await loadHistory(document.getElementById("range-select")?.value || "1h");
  } catch (e) { console.error(e); }
}

function clock() { document.getElementById("clock").textContent = new Date().toLocaleTimeString(); }

document.getElementById("sidebar").addEventListener("click", (e) => {
  const item = e.target.closest(".nav-item");
  if (!item) return;
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  item.classList.add("active");
  currentView = item.dataset.view;
  renderView();
});
document.getElementById("range-select")?.addEventListener("change", (e) => loadHistory(e.target.value));

clock();
tick();
setInterval(tick, 1500);
setInterval(clock, 1000);
