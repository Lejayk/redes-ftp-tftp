"use strict";

// posición horizontal (en %) de cada línea de vida del diagrama
const X = { client: 11, primary: 54, secondary: 90 };
// pausa visual entre paquetes, para que una ráfaga se pueda seguir con la vista
const SPACING = { fast: 90, normal: 280, slow: 620 };
const BACKLOG_LIMIT = 25;
// un poco más que el trazo de tiza (0,42 s) y su rótulo (0,54 s)
const DRAW_LIFETIME = 700;
// lo que tarda el borrador en cruzar el pizarrón
const WIPE_DURATION = 650;
const SVG_NS = "http://www.w3.org/2000/svg";

const LEGENDS = {
  ftp: [
    ["Comandos y respuestas", "--ctrl"],
    ["Datos", "--data"],
    ["Saludo y cierre TCP", "--hand"],
    ["ACK de TCP", "--ack"],
  ],
  tftp: [
    ["Pedido RRQ / WRQ", "--request"],
    ["DATA", "--tdata"],
    ["ACK", "--tack"],
    ["ERROR", "--terror", true],
    ["Retransmisión", "--retrans", true],
  ],
};

const LAYER_NAMES = { eth: "Ethernet", ip: "IP", tcp: "TCP", udp: "UDP", app: "Aplicación" };

const ui = {
  tab: "ftp",
  follow: true,
  speed: "normal",
  mode: "auto",
  busy: false,
  hosts: { client: "10.10.10.10", ftp: "10.10.10.21", tftp: "10.10.10.69" },
  ports: { ftp: null, tftp: null },
  lastT: { ftp: null, tftp: null },
  queue: [],
  pumping: false,
  packets: new Map(),
  selectedId: null,
  ops: { ftp: null, tftp: null },
  lastOps: { ftp: null, tftp: null },
  // la comparativa solo tiene sentido entre descargas que terminaron bien
  downloads: { ftp: null, tftp: null },
  captureWarned: false,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

// íconos del sprite svg de index.html
function icon(name) {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("class", "icon");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS(SVG_NS, "use");
  use.setAttribute("href", `#i-${name}`);
  svg.append(use);
  return svg;
}

function fmtBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toLocaleString("es", { maximumFractionDigits: 1 })} KB`;
}

const scrollBox = (proto) => $(`.wire-scroll[data-proto="${proto}"]`);
const timeline = (proto) => $(".timeline", scrollBox(proto));

/* ---------- conexión en vivo ---------- */

function connect() {
  const scheme = location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${scheme}://${location.host}/ws`);
  socket.onopen = () => setLive(true);
  socket.onclose = () => {
    setLive(false);
    setTimeout(connect, 1500);
  };
  socket.onmessage = (message) => {
    const event = JSON.parse(message.data);
    if (event.type === "state") return applyState(event);
    if (event.type === "history") {
      ui.queue = [];
      resetAll();
      for (const past of event.events) handle(past, false);
      return;
    }
    ui.queue.push(event);
    pump();
  };
}

function setLive(on) {
  const live = $("#live");
  live.classList.toggle("on", on);
  $("b", live).textContent = on ? "En vivo" : "Sin conexión";
}

async function pump() {
  if (ui.pumping) return;
  ui.pumping = true;
  try {
    while (ui.queue.length) {
      const event = ui.queue.shift();
      // el borrador termina de pasar antes de escribir lo siguiente
      await handle(event, true);
      if (event.type !== "packet") continue;
      let wait = SPACING[ui.speed];
      if (event.kind === "ack") wait = document.body.classList.contains("hide-acks") ? 0 : wait * 0.45;
      if (ui.queue.length > BACKLOG_LIMIT) wait = Math.min(wait, 30);
      if (wait) await sleep(wait);
    }
  } finally {
    ui.pumping = false;
  }
}

function handle(event, live) {
  switch (event.type) {
    case "packet":
      return addPacket(event, live);
    case "say":
      return addLog(event);
    case "op":
      return event.phase === "start" ? startOp(event, live) : endOp(event);
    case "waiting":
      return showWaiting(event);
    case "resumed":
      return hideWaiting();
    case "clear":
      return live ? wipeBoard() : resetAll();
    default:
      return undefined;
  }
}

/* ---------- estado del servidor ---------- */

function applyState(state) {
  ui.busy = state.busy;
  ui.mode = state.pacing.mode;
  ui.speed = state.pacing.speed;
  ui.hosts = state.hosts;

  $$("#mode button").forEach((button) => {
    button.classList.toggle("on", button.dataset.mode === ui.mode);
    button.setAttribute("aria-pressed", String(button.dataset.mode === ui.mode));
  });
  $("#speed").value = ui.speed;
  $$("[data-action]").forEach((button) => (button.disabled = state.busy));
  $("#cancel").disabled = !state.busy;
  document.body.classList.toggle("busy", state.busy);

  const pill = $("#ftp-status");
  if (!state.ftp.connected) {
    pill.textContent = "Desconectado";
    pill.className = "pill off";
  } else if (!state.ftp.user) {
    pill.textContent = "Conectado · sin login";
    pill.className = "pill warn";
  } else {
    pill.textContent = `Sesión: ${state.ftp.user}`;
    pill.className = "pill on";
  }

  if (!state.capture.ok && !ui.captureWarned) {
    ui.captureWarned = true;
    toast(`La captura de paquetes no arrancó: ${state.capture.error ?? "sin detalle"}`);
  }
  buildHeads("ftp");
  buildHeads("tftp");
}

/* ---------- cabeceras y líneas de vida ---------- */

function buildHeads(proto) {
  const box = scrollBox(proto);
  const inner = $(".heads-inner", box);
  const server = proto === "ftp" ? ui.hosts.ftp : ui.hosts.tftp;
  const name = proto === "ftp" ? "Servidor FTP" : "Servidor TFTP";
  const secondPort = ui.ports[proto] ?? (proto === "ftp" ? "pasivo" : "TID");
  const defs = [
    ["client", "Cliente", ui.hosts.client, "puerto efímero", "--muted"],
    ["primary", name, `${server}:${proto === "ftp" ? 21 : 69}`, proto === "ftp" ? "canal de control" : "recibe pedidos", proto === "ftp" ? "--ctrl" : "--request"],
    ["secondary", name, `${server}:${secondPort}`, proto === "ftp" ? "canal de datos" : "transferencia (TID)", proto === "ftp" ? "--data" : "--tdata"],
  ];
  inner.replaceChildren();
  for (const [key, title, address, role, color] of defs) {
    const head = el("div", `head h-${key}`);
    head.style.left = `${X[key]}%`;
    head.style.setProperty("--lane-color", `var(${color})`);
    head.append(el("b", "", title), el("code", "", address), el("small", "", role));
    inner.append(head);
  }
  const lifelines = $(".lifelines", box);
  if (!lifelines.childElementCount) {
    for (const x of Object.values(X)) {
      const line = el("i");
      line.style.left = `${x}%`;
      lifelines.append(line);
    }
  }
}

function serverLane(packet) {
  if (packet.proto === "ftp") return packet.channel === "ctrl" ? X.primary : X.secondary;
  return packet.server_port === 69 ? X.primary : X.secondary;
}

function buildLegend() {
  const legend = $("#legend");
  legend.replaceChildren();
  for (const [text, color, dashed] of LEGENDS[ui.tab]) {
    const item = el("span");
    const swatch = el("i", dashed ? "dashed" : "");
    swatch.style.setProperty("--c", `var(${color})`);
    item.append(swatch, text);
    legend.append(item);
  }
}

/* ---------- paquetes ---------- */

function addPacket(packet, live) {
  ui.packets.set(packet.id, packet);
  const op = ui.ops[packet.proto];
  if (op) {
    op.packets += 1;
    op.wire += packet.frame_len;
    op.file += packet.file_bytes || 0;
  }

  const box = scrollBox(packet.proto);
  const stick = box.scrollHeight - box.scrollTop - box.clientHeight < 120;
  const list = timeline(packet.proto);
  $(".empty", list)?.remove();

  const row = el("div", `row k-${packet.kind} c-${packet.channel} d-${packet.dir}`);
  row.dataset.id = packet.id;
  const start = op ? op.t0 : packet.t;
  row.append(el("div", "time", `+${Math.max(0, packet.t - start).toFixed(3)} s`));

  const lanes = el("div", "lanes");
  const server = serverLane(packet);
  const from = packet.dir === "out" ? X.client : server;
  const to = packet.dir === "out" ? server : X.client;
  const left = Math.min(from, to);
  const width = Math.abs(to - from);

  const arrow = el("div", `arrow ${packet.dir}`);
  arrow.style.left = `${left}%`;
  arrow.style.width = `${width}%`;
  arrow.append(el("i", "head"));
  if (live && packet.proto === ui.tab) {
    // la clase se retira con un temporizador y no con animationend: una pestaña oculta
    // pausa las animaciones y, al volver, las repetiría todas juntas
    row.classList.add("draw");
    setTimeout(() => row.classList.remove("draw"), DRAW_LIFETIME);
  }

  const label = el("div", "label");
  if (packet.secret) {
    // la contraseña en texto plano: el profe encierra solo la contraseña en un círculo de tiza
    const [verb, ...rest] = packet.label.split(" ");
    label.append(verb, el("span", "mark-circle", rest.join(" ")));
    row.classList.add("secret");
  } else {
    label.textContent = packet.label;
  }
  const meta = el("div", "meta", packet.meta);
  for (const node of [label, meta]) {
    node.style.left = `${left}%`;
    node.style.width = `${width}%`;
  }
  lanes.append(arrow, label, meta);
  row.append(lanes);
  if (packet.explain) row.append(el("p", "explain", packet.explain));

  // cada fila se abre con clic o con enter/espacio desde el teclado
  row.tabIndex = 0;
  row.setAttribute("role", "button");
  row.setAttribute("aria-label", `${packet.dir === "out" ? "Cliente a servidor" : "Servidor a cliente"}: ${packet.label}`);
  const open = () => {
    setFollow(false);
    inspect(packet.id);
  };
  row.addEventListener("click", open);
  row.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    event.stopPropagation();
    open();
  });

  // el silencio antes de que el servidor reenvíe un bloque se dibuja con su duración
  const previous = ui.lastT[packet.proto];
  if (packet.kind === "retrans" && packet.label.startsWith("DATA") && previous !== null) {
    const seconds = Math.max(0, packet.t - previous);
    const gap = el("div", "gap");
    gap.style.setProperty("--seconds", Math.min(seconds, 6).toFixed(2));
    const text = seconds.toLocaleString("es", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    gap.append(el("span", "", `${text} s de silencio: el ACK nunca llegó`));
    list.append(gap);
  }
  ui.lastT[packet.proto] = packet.t;
  list.append(row);

  if (server === X.secondary && ui.ports[packet.proto] !== packet.server_port) {
    ui.ports[packet.proto] = packet.server_port;
    buildHeads(packet.proto);
  }
  if (stick) box.scrollTop = box.scrollHeight;
  if (ui.follow && packet.kind !== "ack" && packet.proto === ui.tab) inspect(packet.id);
  if (packet.proto === ui.tab) renderStats();
}

/* ---------- operaciones ---------- */

function startOp(event, live) {
  ui.ops[event.proto] = { title: event.title, t0: event.t, packets: 0, wire: 0, file: 0 };
  ui.ports[event.proto] = null;
  buildHeads(event.proto);
  if (live && ui.tab !== event.proto) switchTab(event.proto);
  const list = timeline(event.proto);
  $(".empty", list)?.remove();
  const separator = el("div", "op-sep");
  separator.append(el("span", "", event.title));
  list.append(separator);
  const box = scrollBox(event.proto);
  box.scrollTop = box.scrollHeight;
  renderStats();
}

function endOp(event) {
  const op = ui.ops[event.proto];
  if (!op) return;
  op.ok = event.ok;
  op.duration = Math.max(0, event.t - op.t0);
  ui.lastOps[event.proto] = { ...op };
  if (event.ok && /^(Descargar|Demo completa)/.test(op.title)) ui.downloads[event.proto] = { ...op };
  ui.ops[event.proto] = null;
  const summary = `${op.packets} paquetes · ${fmtBytes(op.wire)} en el cable · ${op.duration.toFixed(2)} s`;
  const end = el("div", `op-end ${event.ok ? "ok" : "fail"}`);
  end.append(icon(event.ok ? "check" : "x"), summary);
  timeline(event.proto).append(end);
  const box = scrollBox(event.proto);
  box.scrollTop = box.scrollHeight;
  renderStats();
}

function renderStats() {
  const stats = $("#stats");
  stats.replaceChildren();
  const op = ui.ops[ui.tab] ?? ui.lastOps[ui.tab];
  if (!op) {
    stats.append(el("span", "muted", "Aquí aparecen los números de cada operación: paquetes, bytes en el cable y cuánto de eso es el archivo."));
  } else {
    const extra = op.wire ? Math.round(((op.wire - op.file) / op.wire) * 100) : 0;
    const items = [
      ["title", ui.ops[ui.tab] ? "En curso" : "Última operación", op.title],
      ["", "Paquetes", op.packets],
      ["", "En el cable", fmtBytes(op.wire)],
      ["", "Del archivo", fmtBytes(op.file)],
      ["", "No es archivo", `${extra}%`],
    ];
    for (const [kind, caption, value] of items) {
      const stat = el("div", `stat ${kind}`);
      stat.append(el("small", "", caption), el("b", "", String(value)));
      if (kind === "title") stat.title = op.title;
      stats.append(stat);
    }
  }
  const { ftp, tftp } = ui.downloads;
  if (ftp && tftp) {
    const compare = el("div", "compare");
    compare.title = `FTP: ${ftp.title}\nTFTP: ${tftp.title}`;
    compare.append(el("span", "cap", "Comparativa · última descarga de cada uno"));
    compare.append(el("b", "ftp", "FTP"), el("span", "", `${ftp.packets} paq.`), el("span", "", fmtBytes(ftp.wire)));
    compare.append(el("b", "tftp", "TFTP"), el("span", "", `${tftp.packets} paq.`), el("span", "", fmtBytes(tftp.wire)));
    stats.append(compare);
  }
}

/* ---------- bitácora ---------- */

function addLog(event) {
  const log = $("#log");
  const item = el("li", event.tone);
  item.append(el("span", `tag ${event.proto}`, event.proto.toUpperCase()), event.text);
  log.append(item);
  while (log.childElementCount > 200) log.firstElementChild.remove();
  log.scrollTop = log.scrollHeight;
}

/* ---------- paso a paso ---------- */

function showWaiting(event) {
  $("#waiting-label").textContent = event.label;
  $("#waiting").hidden = false;
}

function hideWaiting() {
  $("#waiting").hidden = true;
}

/* ---------- inspector ---------- */

function setFollow(on) {
  ui.follow = on;
  $("#follow").classList.toggle("on", on);
  $("#follow").textContent = on ? "En vivo" : "Volver a en vivo";
}

function inspect(id) {
  const packet = ui.packets.get(id);
  if (!packet) return;
  ui.selectedId = id;
  $$(".row.selected").forEach((row) => row.classList.remove("selected"));
  $(`.row[data-id="${id}"]`)?.classList.add("selected");

  const body = $("#insp-body");
  body.className = "insp-body";
  body.replaceChildren();
  const color = getComputedStyle($(`.row[data-id="${id}"]`) ?? document.body).getPropertyValue("--c");
  body.style.setProperty("--c", color);

  const title = el("div", "insp-title");
  const badge = el("span", "badge", packet.transport);
  badge.style.setProperty("--c", color);
  title.append(badge, el("b", "", packet.label));
  const [source, target] = packet.dir === "out" ? [packet.client, packet.server] : [packet.server, packet.client];
  body.append(title, el("div", "insp-route", `${source} → ${target} · ${packet.frame_len} bytes en el cable`));
  if (packet.explain) body.append(el("p", "insp-explain", packet.explain));

  const fieldRows = [];
  const layers = el("div", "layers");
  for (const layer of packet.layers) {
    const details = el("details", `layer l-${layer.key}`);
    details.open = true;
    const summary = el("summary");
    summary.append(el("span", "swatch"), el("b", "", layer.name), el("small", "", `${layer.end - layer.start} B`));
    const list = el("dl");
    for (const field of layer.fields) {
      const row = el("div", "field");
      row.append(el("dt", "", field.label), el("dd", "", field.value));
      if (field.emphasis) row.classList.add("mark");
      list.append(row);
      fieldRows.push({ row, start: field.start, end: field.end, size: field.end - field.start, emphasis: !!field.emphasis });
    }
    details.append(summary, list);
    layers.append(details);
  }
  body.append(layers, buildHex(packet, fieldRows));
}

function buildHex(packet, fieldRows) {
  const bytes = packet.hex.match(/../g) ?? [];
  const layerAt = new Array(bytes.length).fill("");
  for (const layer of packet.layers) {
    for (let i = layer.start; i < Math.min(layer.end, bytes.length); i += 1) layerAt[i] = layer.key;
  }

  const wrap = el("div", "hex");
  wrap.append(el("h3", "", `Bytes en el cable · ${bytes.length}`));
  const grid = el("div", "hexgrid");
  // 16 bytes por línea no entran en un panel angosto sin esconder la columna de texto
  const perLine = $(".inspector").clientWidth > 520 ? 16 : 8;
  grid.style.setProperty("--per-line", perLine);
  const cells = [];
  for (let offset = 0; offset < bytes.length; offset += perLine) {
    const line = el("div", "hexline");
    const hexPart = el("span", "hx");
    const asciiPart = el("span", "asc");
    for (let i = offset; i < Math.min(offset + perLine, bytes.length); i += 1) {
      const layerClass = layerAt[i] ? `l-${layerAt[i]}` : "";
      const code = parseInt(bytes[i], 16);
      const hexCell = el("span", layerClass, bytes[i]);
      const asciiCell = el("span", layerClass, code >= 32 && code < 127 ? String.fromCharCode(code) : "·");
      hexCell.dataset.i = i;
      asciiCell.dataset.i = i;
      hexPart.append(hexCell);
      asciiPart.append(asciiCell);
      cells[i] = [hexCell, asciiCell];
    }
    line.append(el("span", "off", offset.toString(16).padStart(4, "0")), hexPart, asciiPart);
    grid.append(line);
  }

  // lo que el profe marcó en el pizarrón (la contraseña) queda marcado también en los bytes
  for (const field of fieldRows.filter((item) => item.emphasis)) {
    for (let i = field.start; i < field.end; i += 1) cells[i]?.forEach((cell) => cell.classList.add("mark"));
  }

  // resaltado cruzado: pasar sobre un campo marca sus bytes y viceversa
  let active = null;
  const paint = (field, on) => {
    if (!field) return;
    field.row.classList.toggle("hl", on);
    for (let i = field.start; i < field.end; i += 1) cells[i]?.forEach((cell) => cell.classList.toggle("hl", on));
  };
  const activate = (field) => {
    if (active === field) return;
    paint(active, false);
    active = field;
    paint(active, true);
  };
  for (const field of fieldRows) {
    field.row.addEventListener("mouseenter", () => activate(field));
    field.row.addEventListener("mouseleave", () => activate(null));
  }
  grid.addEventListener("mouseover", (event) => {
    const index = Number(event.target.dataset?.i);
    if (Number.isNaN(index)) return;
    const matches = fieldRows.filter((field) => index >= field.start && index < field.end);
    activate(matches.sort((a, b) => a.size - b.size)[0] ?? null);
  });
  grid.addEventListener("mouseleave", () => activate(null));

  const legend = el("div", "hex-legend");
  for (const key of [...new Set(packet.layers.map((layer) => layer.key))]) {
    const item = el("span", `l-${key}`);
    item.append(el("i"), LAYER_NAMES[key] ?? key);
    legend.append(item);
  }
  wrap.append(grid, legend);
  return wrap;
}

/* ---------- pestañas y limpieza ---------- */

function switchTab(proto) {
  ui.tab = proto;
  $$(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === proto);
    tab.setAttribute("aria-selected", String(tab.dataset.tab === proto));
  });
  $$(".controls").forEach((panel) => (panel.hidden = panel.dataset.proto !== proto));
  $$(".wire-scroll").forEach((box) => (box.hidden = box.dataset.proto !== proto));
  buildLegend();
  renderStats();
}

let wiping = false;
function wipeBoard() {
  const board = $("#board");
  if (wiping || matchMedia("(prefers-reduced-motion: reduce)").matches) {
    resetAll();
    return Promise.resolve();
  }
  wiping = true;
  board.classList.add("wiping");
  return new Promise((resolve) => {
    setTimeout(() => {
      resetAll();
      board.classList.remove("wiping");
      wiping = false;
      resolve();
    }, WIPE_DURATION);
  });
}

function resetAll() {
  ui.lastT = { ftp: null, tftp: null };
  for (const proto of ["ftp", "tftp"]) {
    const list = timeline(proto);
    $$(".row, .op-sep, .op-end, .gap, .empty", list).forEach((node) => node.remove());
    const empty = el("div", "empty");
    empty.innerHTML =
      proto === "ftp"
        ? "Empieza con <b>Demo completa</b> o sigue los pasos 1 a 6 del cliente FTP."
        : "Elige un archivo y pulsa <b>Descargar RRQ</b>.";
    list.append(empty);
    ui.ops[proto] = null;
    ui.lastOps[proto] = null;
    ui.downloads[proto] = null;
    ui.ports[proto] = null;
    buildHeads(proto);
  }
  ui.packets.clear();
  ui.selectedId = null;
  $("#log").replaceChildren();
  const body = $("#insp-body");
  body.className = "insp-body insp-empty";
  body.textContent = "Haz clic en cualquier flecha para abrir el paquete capa por capa, hasta el último byte.";
  hideWaiting();
  renderStats();
}

/* ---------- acciones ---------- */

let toastTimer = null;
function toast(message) {
  const box = $("#toast");
  box.textContent = message;
  box.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (box.hidden = true), 4500);
}

async function post(path, body = {}) {
  try {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      toast(typeof data.detail === "string" ? data.detail : "Revisa los campos: hay un valor que no es válido.");
    }
  } catch {
    toast("No hay conexión con el cliente. ¿Está corriendo Docker?");
  }
}

const value = (id) => $(`#${id}`).value.trim();

const ACTIONS = {
  "ftp.demo": () => post("/api/ftp/demo"),
  "ftp.connect": () => post("/api/ftp/connect"),
  "ftp.login": () => post("/api/ftp/login", { user: value("ftp-user"), password: $("#ftp-pass").value }),
  "ftp.list": () => post("/api/ftp/list"),
  "ftp.download": () => post("/api/ftp/download", { filename: value("ftp-file") }),
  "ftp.upload": () => post("/api/ftp/upload", { filename: value("ftp-up-name"), size: value("ftp-up-size") }),
  "ftp.raw": () => post("/api/ftp/raw", { command: value("ftp-raw") }),
  "ftp.quit": () => post("/api/ftp/quit"),
  "tftp.download": () => post("/api/tftp/download", { filename: value("tftp-file"), lose_ack: $("#tftp-lose").checked }),
  "tftp.upload": () => post("/api/tftp/upload", { filename: value("tftp-up-name"), size: value("tftp-up-size") }),
};

function sendPacing() {
  post("/api/pacing", { mode: ui.mode, speed: ui.speed });
}

function bindControls() {
  $$("[data-action]").forEach((button) =>
    button.addEventListener("click", () => {
      button.blur();
      ACTIONS[button.dataset.action]();
    }),
  );
  $$(".tab").forEach((tab) => tab.addEventListener("click", () => switchTab(tab.dataset.tab)));
  $$("#mode button").forEach((button) =>
    button.addEventListener("click", () => {
      ui.mode = button.dataset.mode;
      sendPacing();
    }),
  );
  $("#speed").addEventListener("change", (event) => {
    ui.speed = event.target.value;
    sendPacing();
  });
  $$(".chip").forEach((chip) => chip.addEventListener("click", () => ($("#tftp-file").value = chip.dataset.file)));
  $("#next").addEventListener("click", () => post("/api/next"));
  $("#cancel").addEventListener("click", () => post("/api/cancel"));
  $("#clear").addEventListener("click", () => post("/api/clear"));
  $("#follow").addEventListener("click", () => {
    setFollow(!ui.follow);
    if (!ui.follow) return;
    const last = [...ui.packets.values()].reverse().find((packet) => packet.proto === ui.tab && packet.kind !== "ack");
    if (last) inspect(last.id);
  });
  $("#show-acks").addEventListener("change", (event) => document.body.classList.toggle("hide-acks", !event.target.checked));
  $("#show-explain").addEventListener("change", (event) => document.body.classList.toggle("hide-explain", !event.target.checked));
  $("#theme").addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(next);
    try {
      localStorage.setItem("theme", next);
    } catch {
      // sin almacenamiento local el tema simplemente no se recuerda
    }
  });

  // enter dentro de un campo dispara la acción de su paso
  const enterActions = { "ftp-raw": "ftp.raw", "ftp-pass": "ftp.login", "ftp-file": "ftp.download", "tftp-file": "tftp.download" };
  for (const [id, action] of Object.entries(enterActions)) {
    $(`#${id}`).addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !ui.busy) ACTIONS[action]();
    });
  }

  // un presentador de diapositivas manda flecha derecha o avpág: sirven para avanzar el paso
  document.addEventListener("keydown", (event) => {
    if (event.target.matches("input, select, textarea")) return;
    if (!["ArrowRight", "PageDown", " ", "Enter"].includes(event.key)) return;
    if ($("#waiting").hidden) return;
    event.preventDefault();
    post("/api/next");
  });
}

// oscuro es el pizarrón verde; claro, la pizarra blanca
function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const label = theme === "dark" ? "Cambiar a pizarra blanca" : "Cambiar a pizarrón";
  $("#theme").title = label;
  $("#theme").setAttribute("aria-label", label);
}

function init() {
  // primero la elección guardada; si no hay, la del sistema operativo
  let theme = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  try {
    const saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") theme = saved;
  } catch {
    // sin almacenamiento local se usa la preferencia del sistema
  }
  applyTheme(theme);
  bindControls();
  buildHeads("ftp");
  buildHeads("tftp");
  buildLegend();
  renderStats();
  connect();
}

init();
