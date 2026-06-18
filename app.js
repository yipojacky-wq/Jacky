const STORAGE_KEY = "jasic-watchlist-v2";
const BUY_SCORE_THRESHOLD = 68;

const sampleStocks = [
  {
    id: crypto.randomUUID(),
    symbol: "2330",
    name: "台積電",
    price: 920,
    target: 1050,
    growth: 14.2,
    pe: 22,
    momentum: 7.5,
    risk: 2,
    notes: "AI 與先進製程需求穩定，留意匯率與法說展望。"
  },
  {
    id: crypto.randomUUID(),
    symbol: "2454",
    name: "聯發科",
    price: 1240,
    target: 1380,
    growth: 9.8,
    pe: 18,
    momentum: 3.9,
    risk: 2,
    notes: "手機與邊緣 AI 題材，觀察毛利率。"
  },
  {
    id: crypto.randomUUID(),
    symbol: "AAPL",
    name: "Apple",
    price: 196,
    target: 214,
    growth: 3.1,
    pe: 29,
    momentum: -1.8,
    risk: 1,
    notes: "成熟大型股，評估新產品與服務收入。"
  }
];

const state = {
  stocks: loadStocks(),
  editingId: null,
  sortBy: "score",
  query: ""
};

const form = document.querySelector("#stockForm");
const rows = document.querySelector("#stockRows");
const chart = document.querySelector("#scoreChart");
const ctx = chart.getContext("2d");

const fields = {
  symbol: document.querySelector("#symbol"),
  name: document.querySelector("#name"),
  price: document.querySelector("#price"),
  target: document.querySelector("#target"),
  growth: document.querySelector("#growth"),
  pe: document.querySelector("#pe"),
  momentum: document.querySelector("#momentum"),
  risk: document.querySelector("#risk"),
  notes: document.querySelector("#notes")
};

function loadStocks() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveStocks() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.stocks));
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function getUpside(stock) {
  if (!stock.price) return 0;
  return ((stock.target - stock.price) / stock.price) * 100;
}

function getScore(stock) {
  const upside = clamp(getUpside(stock), -40, 60);
  const growth = clamp(stock.growth, -30, 40);
  const pePenalty = clamp((stock.pe - 25) * 0.8, 0, 28);
  const momentum = clamp(stock.momentum, -25, 25);
  const riskPenalty = (Number(stock.risk) - 1) * 7;
  return Math.round(clamp(50 + upside * 0.65 + growth * 0.9 + momentum * 0.55 - pePenalty - riskPenalty, 0, 100));
}

function getSignal(score) {
  if (score >= BUY_SCORE_THRESHOLD) return { label: "買進觀察", className: "buy" };
  if (score >= 52) return { label: "持續追蹤", className: "watch" };
  return { label: "暫緩", className: "avoid" };
}

function getRiskLabel(risk) {
  return { 1: "低", 2: "中", 3: "高" }[risk] || "中";
}

function formatPercent(value) {
  const fixed = Number(value).toFixed(1);
  return `${value > 0 ? "+" : ""}${fixed}%`;
}

function getVisibleStocks() {
  const query = state.query.trim().toLowerCase();
  const stocks = state.stocks.filter((stock) => {
    if (!query) return true;
    return [stock.symbol, stock.name, stock.notes].some((value) =>
      String(value || "").toLowerCase().includes(query)
    );
  });

  return stocks.sort((a, b) => {
    if (state.sortBy === "symbol") return a.symbol.localeCompare(b.symbol);
    if (state.sortBy === "risk") return b.risk - a.risk;
    if (state.sortBy === "upside") return getUpside(b) - getUpside(a);
    return getScore(b) - getScore(a);
  });
}

function renderMetrics(stocks) {
  const scores = stocks.map(getScore);
  const avg = scores.length ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : 0;
  document.querySelector("#totalCount").textContent = stocks.length;
  document.querySelector("#avgScore").textContent = avg;
  document.querySelector("#buyCount").textContent = scores.filter((score) => score >= BUY_SCORE_THRESHOLD).length;
  document.querySelector("#riskCount").textContent = stocks.filter((stock) => Number(stock.risk) === 3).length;
}

function renderTable(stocks) {
  rows.innerHTML = "";

  if (!stocks.length) {
    const template = document.querySelector("#emptyTemplate");
    rows.append(template.content.cloneNode(true));
    const loadSampleBtn = document.querySelector("#loadSampleBtn");
    loadSampleBtn?.addEventListener("click", () => {
      state.stocks = sampleStocks.map((stock) => ({ ...stock, id: crypto.randomUUID() }));
      saveStocks();
      render();
    });
    return;
  }

  const fragment = document.createDocumentFragment();
  stocks.forEach((stock) => {
    const score = getScore(stock);
    const signal = getSignal(score);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>
        <div class="symbol">
          <strong>${escapeHtml(stock.symbol)} ${escapeHtml(stock.name)}</strong>
          <small class="notes">${escapeHtml(stock.notes || "無備註")}</small>
        </div>
      </td>
      <td>${Number(stock.price).toFixed(2)}</td>
      <td>${Number(stock.target).toFixed(2)}</td>
      <td>${formatPercent(getUpside(stock))}</td>
      <td><span class="score">${score}</span></td>
      <td><span class="signal ${signal.className}">${signal.label}</span></td>
      <td><span class="risk-pill">${getRiskLabel(stock.risk)}</span></td>
      <td>
        <div class="row-actions">
          <button type="button" data-action="edit" data-id="${stock.id}">編輯</button>
          <button type="button" class="delete" data-action="delete" data-id="${stock.id}">刪除</button>
        </div>
      </td>
    `;
    fragment.append(tr);
  });

  rows.append(fragment);
}

function renderChart(stocks) {
  const dpr = window.devicePixelRatio || 1;
  const rect = chart.getBoundingClientRect();
  chart.width = Math.max(360, rect.width * dpr);
  chart.height = 280 * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  const width = chart.width / dpr;
  const height = chart.height / dpr;
  ctx.clearRect(0, 0, width, height);

  if (!stocks.length) {
    ctx.fillStyle = "#62706a";
    ctx.font = "15px Segoe UI";
    ctx.fillText("新增股票後會顯示評分圖表", 24, 56);
    return;
  }

  const topStocks = stocks.slice(0, 8);
  const padding = { top: 24, right: 20, bottom: 42, left: 42 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const gap = 12;
  const barWidth = Math.max(20, (plotWidth - gap * (topStocks.length - 1)) / topStocks.length);

  ctx.strokeStyle = "#d9e3df";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i += 1) {
    const y = padding.top + plotHeight - (plotHeight * i) / 4;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();
  }

  topStocks.forEach((stock, index) => {
    const score = getScore(stock);
    const x = padding.left + index * (barWidth + gap);
    const barHeight = (score / 100) * plotHeight;
    const y = padding.top + plotHeight - barHeight;
    const gradient = ctx.createLinearGradient(0, y, 0, padding.top + plotHeight);
    gradient.addColorStop(0, "#0f766e");
    gradient.addColorStop(1, "#89b8a9");
    ctx.fillStyle = gradient;
    ctx.fillRect(x, y, barWidth, barHeight);

    ctx.fillStyle = "#17211d";
    ctx.font = "700 13px Segoe UI";
    ctx.textAlign = "center";
    ctx.fillText(score, x + barWidth / 2, y - 7);

    ctx.fillStyle = "#62706a";
    ctx.font = "12px Segoe UI";
    ctx.fillText(stock.symbol, x + barWidth / 2, height - 18);
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function render() {
  const visibleStocks = getVisibleStocks();
  renderMetrics(state.stocks);
  renderTable(visibleStocks);
  renderChart(visibleStocks);
}

function readForm() {
  return {
    symbol: fields.symbol.value.trim().toUpperCase(),
    name: fields.name.value.trim(),
    price: Number(fields.price.value),
    target: Number(fields.target.value),
    growth: Number(fields.growth.value),
    pe: Number(fields.pe.value),
    momentum: Number(fields.momentum.value),
    risk: Number(fields.risk.value),
    notes: fields.notes.value.trim()
  };
}

function fillForm(stock) {
  Object.entries(fields).forEach(([key, field]) => {
    field.value = stock[key] ?? "";
  });
}

function resetForm() {
  form.reset();
  fields.risk.value = "2";
  state.editingId = null;
  document.querySelector("#submitBtn").textContent = "加入觀察";
  document.querySelector("#editState").textContent = "新增模式";
  document.querySelector("#cancelEditBtn").hidden = true;
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  const [, ...dataRows] = lines;
  return dataRows.map((line) => {
    const [symbol, name, price, target, growth, pe, momentum, risk, notes] = parseCsvLine(line);
    return {
      id: crypto.randomUUID(),
      symbol: (symbol || "").trim().toUpperCase(),
      name: (name || "").trim(),
      price: Number(price),
      target: Number(target),
      growth: Number(growth),
      pe: Number(pe),
      momentum: Number(momentum),
      risk: Number(risk || 2),
      notes: (notes || "").trim()
    };
  }).filter((stock) => stock.symbol && stock.name && Number.isFinite(stock.price));
}

function parseCsvLine(line) {
  const values = [];
  let value = "";
  let quoted = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    const next = line[i + 1];

    if (char === '"' && quoted && next === '"') {
      value += '"';
      i += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(value);
      value = "";
    } else {
      value += char;
    }
  }

  values.push(value);
  return values;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const stock = readForm();
  if (state.editingId) {
    state.stocks = state.stocks.map((item) => item.id === state.editingId ? { ...stock, id: item.id } : item);
  } else {
    state.stocks = [{ ...stock, id: crypto.randomUUID() }, ...state.stocks];
  }
  saveStocks();
  resetForm();
  render();
});

rows.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const stock = state.stocks.find((item) => item.id === button.dataset.id);
  if (!stock) return;

  if (button.dataset.action === "edit") {
    state.editingId = stock.id;
    fillForm(stock);
    document.querySelector("#submitBtn").textContent = "儲存變更";
    document.querySelector("#editState").textContent = `編輯 ${stock.symbol}`;
    document.querySelector("#cancelEditBtn").hidden = false;
    fields.symbol.focus();
  }

  if (button.dataset.action === "delete") {
    state.stocks = state.stocks.filter((item) => item.id !== stock.id);
    saveStocks();
    render();
  }
});

document.querySelector("#cancelEditBtn").addEventListener("click", resetForm);

document.querySelector("#sortBy").addEventListener("change", (event) => {
  state.sortBy = event.target.value;
  render();
});

document.querySelector("#searchInput").addEventListener("input", (event) => {
  state.query = event.target.value;
  render();
});

document.querySelector("#exportBtn").addEventListener("click", () => {
  const header = "symbol,name,price,target,growth,pe,momentum,risk,notes";
  const csvRows = state.stocks.map((stock) =>
    [stock.symbol, stock.name, stock.price, stock.target, stock.growth, stock.pe, stock.momentum, stock.risk, stock.notes]
      .map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`)
      .join(",")
  );
  const blob = new Blob([[header, ...csvRows].join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "jasic-watchlist.csv";
  anchor.click();
  URL.revokeObjectURL(url);
});

document.querySelector("#csvInput").addEventListener("change", async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  const text = await file.text();
  const imported = parseCsv(text);
  state.stocks = [...imported, ...state.stocks];
  saveStocks();
  event.target.value = "";
  render();
});

window.addEventListener("resize", render);

render();
