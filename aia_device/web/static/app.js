// Poll de /api/metrics cada 1.5s y render de tablas.
const fmt = (v, unit = "") => (v === null || v === undefined) ? '<span class="na">N/A</span>' : `${v}${unit}`;

function row(t, k, v) {
  return `<tr><td class="k">${k}</td><td class="v">${v}</td></tr>`;
}

function renderCpu(d) {
  if (!d) return "";
  return row("", "Uso", fmt(d.usage_percent, " %"))
    + row("", "Load 1/5/15", `${fmt(d.load["1"])} / ${fmt(d.load["5"])} / ${fmt(d.load["15"])}`)
    + row("", "Núcleos/Hilos", `${d.cores}c / ${d.threads}t`)
    + row("", "Temp", fmt(d.temp_c, " °C"));
}

function renderGpu(d) {
  if (!d || !d.available) return row("", "GPU", '<span class="na">N/A (sin nvidia-smi)</span>');
  return row("", "Uso", fmt(d.usage_percent, " %"))
    + row("", "VRAM", `${fmt(d.mem_used_mb, " MB")} / ${fmt(d.mem_total_mb, " MB")}`)
    + row("", "Watts", fmt(d.power_w, " W"))
    + row("", "Límite", fmt(d.power_limit_w, " W"))
    + row("", "Temp", fmt(d.temp_c, " °C"));
}

function renderPower(d) {
  if (!d) return "";
  return row("", "CPU (RAPL)", fmt(d.cpu_w, " W"))
    + row("", "GPU", fmt(d.gpu_w, " W"))
    + row("", "Total", fmt(d.total_w, " W"));
}

function renderRam(d) {
  if (!d) return "";
  return row("", "Usado", `${fmt(d.used_gb, " GB")} / ${fmt(d.total_gb, " GB")}`)
    + row("", "Uso", fmt(d.usage_percent, " %"))
    + row("", "Temp DIMM", fmt(d.temp_c, " °C"));
}

function renderDisk(d) {
  if (!d) return "";
  return row("", "Uso", `${fmt(d.used_gb, " GB")} / ${fmt(d.total_gb, " GB")} (${fmt(d.usage_percent, " %")})`)
    + row("", "Lectura", fmt(d.read_mbps, " MB/s"))
    + row("", "Escritura", fmt(d.write_mbps, " MB/s"))
    + row("", "Temp", fmt(d.temp_c, " °C"));
}

function renderTemps(d) {
  if (!d) return "";
  return row("", "CPU", fmt(d.cpu_c, " °C"))
    + row("", "GPU", fmt(d.gpu_c, " °C"))
    + row("", "RAM", fmt(d.ram_c, " °C"))
    + row("", "Disco", fmt(d.disk_c, " °C"));
}

function renderNet(d) {
  if (!d) return "";
  let html = `<tr><td class="k">iface</td><td class="v">RX</td><td class="v">TX</td></tr>`;
  for (const [name, v] of Object.entries(d.interfaces)) {
    const tag = v.is_default ? " (internet)" : "";
    html += `<tr><td class="k">${name}${tag}</td><td class="v">${fmt(v.rx_kbps, " KB/s")}</td><td class="v">${fmt(v.tx_kbps, " KB/s")}</td></tr>`;
  }
  return html;
}

async function tick() {
  try {
    const r = await fetch("/api/metrics");
    const m = await r.json();
    document.getElementById("ts").textContent = new Date((m.timestamp || Date.now() / 1000) * 1000).toLocaleTimeString();
    document.getElementById("cpu").innerHTML = renderCpu(m.cpu);
    document.getElementById("gpu").innerHTML = renderGpu(m.gpu);
    document.getElementById("power").innerHTML = renderPower(m.power);
    document.getElementById("ram").innerHTML = renderRam(m.ram);
    document.getElementById("disk").innerHTML = renderDisk(m.disk);
    document.getElementById("temps").innerHTML = renderTemps(m.temps);
    document.getElementById("net").innerHTML = renderNet(m.net);
  } catch (e) {
    document.getElementById("ts").textContent = "error: " + e;
  }
}

tick();
setInterval(tick, 1500);
