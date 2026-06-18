const TWSE_DAILY_URL = "https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL?response=json";
const TWSE_HISTORY_URL = "https://www.twse.com.tw/exchangeReport/STOCK_DAY";
const TWSE_VALUE_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d";
const REALTIME_QUOTES_URL = "data/realtime-quotes.json";
const STORAGE_KEY = "jasic-watchlist-v3";
const AUTO_REFRESH_MS = 5 * 60 * 1000;
const DEFAULT_WATCH_SYMBOLS = ["2327", "2408", "2303"];

const state = {
  catalog: [],
  valuations: new Map(),
  realtimeQuotes: new Map(),
  realtimeGeneratedAt: "",
  watchSymbols: loadWatchSymbols(),
  stocks: [],
  filter: "all",
  loading: false,
  latestDate: ""
};

const elements = {
  form: document.querySelector("#stockSearchForm"),
  input: document.querySelector("#stockSearchInput"),
  results: document.querySelector("#searchResults"),
  clear: document.querySelector("#clearSearchBtn"),
  board: document.querySelector("#stockBoard"),
  empty: document.querySelector("#emptyState"),
  loading: document.querySelector("#loadingState"),
  refresh: document.querySelector("#refreshBtn"),
  status: document.querySelector("#updateStatus"),
  filter: document.querySelector("#signalFilter"),
  template: document.querySelector("#stockCardTemplate")
};

function loadWatchSymbols() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw === null) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_WATCH_SYMBOLS));
      return [...DEFAULT_WATCH_SYMBOLS];
    }
    const saved = JSON.parse(raw);
    return Array.isArray(saved) ? saved : [];
  } catch {
    return [...DEFAULT_WATCH_SYMBOLS];
  }
}

function saveWatchSymbols() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.watchSymbols));
}

function toNumber(value) {
  if (value === undefined || value === null) return null;
  const normalized = String(value).replaceAll(",", "").replace(/[＋+]/g, "").trim();
  if (!normalized || normalized === "--" || normalized === "-") return null;
  const number = Number(normalized);
  return Number.isFinite(number) ? number : null;
}

function formatPrice(value) {
  if (!Number.isFinite(value)) return "--";
  return value >= 100 ? value.toFixed(1) : value.toFixed(2);
}

function formatPercent(value) {
  if (!Number.isFinite(value)) return "--";
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
}

function formatDate(date) {
  if (!date || date.length !== 8) return date || "--";
  return `${date.slice(0, 4)}/${date.slice(4, 6)}/${date.slice(6, 8)}`;
}

function fetchJson(url) {
  return fetch(url, { cache: "no-store" }).then((response) => {
    if (!response.ok) throw new Error(`資料服務回應 ${response.status}`);
    return response.json();
  });
}

async function loadMarketCatalog() {
  const payload = await fetchJson(TWSE_DAILY_URL);
  if (payload.stat !== "OK" || !Array.isArray(payload.data)) {
    throw new Error(payload.stat || "目前無法取得證交所行情");
  }

  state.latestDate = payload.date;
  state.catalog = payload.data
    .filter((row) => /^\d{4}$/.test(row[0]))
    .map((row) => ({
      symbol: row[0],
      name: String(row[1]).replace(/\*+$/, ""),
      volume: toNumber(row[2]),
      open: toNumber(row[4]),
      high: toNumber(row[5]),
      low: toNumber(row[6]),
      close: toNumber(row[7]),
      change: toNumber(row[8]),
      transactions: toNumber(row[9]),
      date: payload.date
    }));

  await loadValuations(payload.date);
}

async function loadValuations(date) {
  const url = `${TWSE_VALUE_URL}?response=json&date=${date}&selectType=ALL`;
  try {
    const payload = await fetchJson(url);
    if (payload.stat !== "OK" || !Array.isArray(payload.data)) return;
    state.valuations = new Map(payload.data.map((row) => [
      row[0],
      {
        dividendYield: toNumber(row[3]),
        pe: toNumber(row[5]),
        pb: toNumber(row[6])
      }
    ]));
  } catch {
    state.valuations = new Map();
  }
}

async function loadRealtimeQuotes() {
  try {
    const payload = await fetchJson(`${REALTIME_QUOTES_URL}?t=${Date.now()}`);
    const quotes = Array.isArray(payload.quotes) ? payload.quotes : [];
    state.realtimeQuotes = new Map(quotes.map((quote) => [quote.symbol, quote]));
    state.realtimeGeneratedAt = payload.generatedAt || "";
    if (!quotes.length) throw new Error("即時報價資料檔尚未產生");
  } catch {
    state.realtimeQuotes = new Map();
    state.realtimeGeneratedAt = "";
  }
}

function getMonthKeys(dateString, count = 3) {
  const year = Number(dateString.slice(0, 4));
  const month = Number(dateString.slice(4, 6));
  const keys = [];
  for (let offset = 0; offset < count; offset += 1) {
    const date = new Date(year, month - 1 - offset, 1);
    keys.push(`${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, "0")}01`);
  }
  return keys;
}

async function loadHistory(symbol) {
  const monthKeys = getMonthKeys(state.latestDate, 3);
  const payloads = await Promise.all(monthKeys.map((date) => {
    const url = `${TWSE_HISTORY_URL}?response=json&date=${date}&stockNo=${symbol}`;
    return fetchJson(url).catch(() => null);
  }));

  const rows = payloads
    .filter((payload) => payload?.stat === "OK" && Array.isArray(payload.data))
    .flatMap((payload) => payload.data.map((row) => ({
      date: row[0],
      volume: toNumber(row[1]),
      open: toNumber(row[3]),
      high: toNumber(row[4]),
      low: toNumber(row[5]),
      close: toNumber(row[6]),
      change: toNumber(row[7])
    })))
    .filter((row) => Number.isFinite(row.close))
    .sort((a, b) => rocDateToKey(a.date).localeCompare(rocDateToKey(b.date)));

  const unique = new Map(rows.map((row) => [row.date, row]));
  return [...unique.values()];
}

function rocDateToKey(value) {
  const [rocYear, month, day] = String(value).split("/");
  return `${Number(rocYear) + 1911}${month}${day}`;
}

function average(values) {
  const valid = values.filter(Number.isFinite);
  if (!valid.length) return null;
  return valid.reduce((sum, value) => sum + value, 0) / valid.length;
}

function calculateRsi(closes, period = 14) {
  if (closes.length <= period) return null;
  const recent = closes.slice(-(period + 1));
  let gains = 0;
  let losses = 0;

  for (let i = 1; i < recent.length; i += 1) {
    const difference = recent[i] - recent[i - 1];
    if (difference >= 0) gains += difference;
    else losses += Math.abs(difference);
  }

  const averageGain = gains / period;
  const averageLoss = losses / period;
  if (averageLoss === 0) return 100;
  const relativeStrength = averageGain / averageLoss;
  return 100 - (100 / (1 + relativeStrength));
}

function calculateIndicators(history, market) {
  const adjustedHistory = [...history];
  if (market.isRealtime && Number.isFinite(market.close)) {
    const latest = adjustedHistory.at(-1);
    if (latest && rocDateToKey(latest.date) === market.date) {
      adjustedHistory[adjustedHistory.length - 1] = { ...latest, close: market.close, volume: market.volume };
    } else {
      adjustedHistory.push({
        date: market.date,
        close: market.close,
        volume: market.volume
      });
    }
  }

  const closes = adjustedHistory.map((item) => item.close);
  const volumes = adjustedHistory.map((item) => item.volume);
  const current = closes.at(-1) ?? market.close;
  const ma5 = average(closes.slice(-5));
  const ma20 = average(closes.slice(-20));
  const rsi = calculateRsi(closes);
  const previous20 = closes.at(-21);
  const momentum20 = Number.isFinite(previous20) ? ((current - previous20) / previous20) * 100 : null;
  const volume5 = average(volumes.slice(-5));
  const volume20 = average(volumes.slice(-20));
  const volumeRatio = Number.isFinite(volume5) && Number.isFinite(volume20) && volume20 !== 0
    ? volume5 / volume20
    : null;

  return { current, ma5, ma20, rsi, momentum20, volumeRatio };
}

function evaluateSignal(indicators, market) {
  let score = 0;
  const reasons = [];
  const { current, ma5, ma20, rsi, momentum20, volumeRatio } = indicators;

  if (Number.isFinite(ma20)) {
    if (current > ma20) {
      score += 2;
      reasons.push({ type: "positive", text: `現價站上 MA20（${formatPrice(ma20)}），中短期趨勢偏多。` });
    } else {
      score -= 2;
      reasons.push({ type: "negative", text: `現價跌破 MA20（${formatPrice(ma20)}），中短期趨勢承壓。` });
    }
  }

  if (Number.isFinite(ma5) && Number.isFinite(ma20)) {
    if (ma5 > ma20) {
      score += 1;
      reasons.push({ type: "positive", text: "MA5 高於 MA20，短線動能相對強勢。" });
    } else {
      score -= 1;
      reasons.push({ type: "negative", text: "MA5 低於 MA20，短線尚未轉強。" });
    }
  }

  if (Number.isFinite(rsi)) {
    if (rsi >= 50 && rsi <= 70) {
      score += 1;
      reasons.push({ type: "positive", text: `RSI 為 ${rsi.toFixed(1)}，多方力道偏強但尚未明顯過熱。` });
    } else if (rsi > 75) {
      score -= 1;
      reasons.push({ type: "neutral", text: `RSI 為 ${rsi.toFixed(1)}，走勢強但短線可能過熱。` });
    } else if (rsi < 35) {
      score -= 1;
      reasons.push({ type: "negative", text: `RSI 為 ${rsi.toFixed(1)}，目前賣壓較重。` });
    } else {
      reasons.push({ type: "neutral", text: `RSI 為 ${rsi.toFixed(1)}，多空力道接近中性。` });
    }
  }

  if (Number.isFinite(momentum20)) {
    if (momentum20 > 3) score += 1;
    if (momentum20 < -3) score -= 1;
    reasons.push({
      type: momentum20 > 3 ? "positive" : momentum20 < -3 ? "negative" : "neutral",
      text: `近 20 日漲跌為 ${formatPercent(momentum20)}，${momentum20 > 3 ? "動能向上" : momentum20 < -3 ? "動能向下" : "目前處於整理區間"}。`
    });
  }

  if (Number.isFinite(volumeRatio) && volumeRatio > 1.25) {
    reasons.push({
      type: market.change >= 0 ? "positive" : "negative",
      text: `近期量比 ${volumeRatio.toFixed(2)}，量能放大且當日${market.change >= 0 ? "收漲" : "收跌"}。`
    });
  }

  if (score >= 3) return { key: "buy", title: "買進觀察", score, reasons };
  if (score <= -3) return { key: "sell", title: "拋售警示", score, reasons };
  return { key: "hold", title: "可持有", score, reasons };
}

async function buildStock(symbol) {
  const dailyMarket = state.catalog.find((item) => item.symbol === symbol);
  if (!dailyMarket) throw new Error(`找不到上市股票 ${symbol}`);
  const quote = state.realtimeQuotes.get(symbol);
  const market = mergeRealtimeQuote(dailyMarket, quote);
  const history = await loadHistory(symbol);
  const indicators = calculateIndicators(history, market);
  const signal = evaluateSignal(indicators, market);
  const valuation = state.valuations.get(symbol) || {};
  return { ...market, history, indicators, signal, valuation };
}

function mergeRealtimeQuote(daily, quote) {
  if (!quote || !Number.isFinite(quote.price)) {
    return {
      ...daily,
      previousClose: daily.close,
      isRealtime: false
    };
  }
  const previousClose = Number.isFinite(quote.previousClose) ? quote.previousClose : daily.close;
  return {
    ...daily,
    previousClose,
    close: quote.price,
    change: Number.isFinite(previousClose) ? quote.price - previousClose : daily.change,
    open: quote.open ?? daily.open,
    high: quote.high ?? daily.high,
    low: quote.low ?? daily.low,
    volume: quote.volume ?? daily.volume,
    date: quote.date || daily.date,
    quoteTime: quote.time || "",
    isRealtime: true
  };
}

async function refreshAll(options = {}) {
  if (state.loading) return;
  setLoading(true);
  clearError();

  try {
    await loadMarketCatalog();
    await loadRealtimeQuotes();
    const results = await Promise.allSettled(state.watchSymbols.map(buildStock));
    state.stocks = results
      .filter((result) => result.status === "fulfilled")
      .map((result) => result.value);

    const failed = results.filter((result) => result.status === "rejected");
    if (failed.length) showError(`有 ${failed.length} 檔股票暫時無法更新，請稍後再試。`);

    render();
    const realtimeTimes = state.stocks.map((stock) => stock.quoteTime).filter(Boolean).sort();
    const latestQuoteTime = realtimeTimes.at(-1);
    const checkedAt = new Date().toLocaleTimeString("zh-TW", { hour: "2-digit", minute: "2-digit" });
    elements.status.textContent = latestQuoteTime
      ? `今日盤價・最後更新 ${latestQuoteTime}`
      : `即時報價未啟用・目前顯示 ${formatDate(state.latestDate)} 收盤`;
    elements.status.classList.toggle("quote-warning", !latestQuoteTime);
    if (!latestQuoteTime) {
      showError("即時報價尚未啟用。請確認 GitHub Pages 的 Source 已改為 GitHub Actions，且 Actions 工作流程執行成功。");
    }
  } catch (error) {
    showError(`無法取得證交所資料：${error.message}`);
    elements.status.textContent = "資料更新失敗";
  } finally {
    setLoading(false);
    if (options.focusSearch) elements.input.focus();
  }
}

function setLoading(loading) {
  state.loading = loading;
  elements.refresh.classList.toggle("is-loading", loading);
  elements.refresh.disabled = loading;
  elements.loading.hidden = !loading || state.watchSymbols.length === 0;
  if (loading && state.watchSymbols.length > 0) elements.empty.hidden = true;
}

function showError(message) {
  clearError();
  const banner = document.createElement("div");
  banner.className = "error-banner";
  banner.id = "errorBanner";
  banner.textContent = message;
  document.querySelector(".watch-section").prepend(banner);
}

function clearError() {
  document.querySelector("#errorBanner")?.remove();
}

function searchCatalog(query) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return [];
  return state.catalog
    .filter((stock) =>
      stock.symbol.toLowerCase().includes(normalized) ||
      stock.name.toLowerCase().includes(normalized)
    )
    .slice(0, 8);
}

function renderSearchResults(matches, query) {
  elements.results.innerHTML = "";
  if (!query.trim()) {
    elements.results.hidden = true;
    return;
  }

  if (!state.catalog.length) {
    elements.results.innerHTML = '<div class="search-message">股票名單載入中，請稍候…</div>';
  } else if (!matches.length) {
    elements.results.innerHTML = '<div class="search-message">找不到相符的上市股票</div>';
  } else {
    matches.forEach((stock) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "search-result";
      button.dataset.symbol = stock.symbol;
      button.setAttribute("role", "option");
      button.innerHTML = `<span>${escapeHtml(stock.name)}</span><strong>${escapeHtml(stock.symbol)}</strong>`;
      elements.results.append(button);
    });
  }
  elements.results.hidden = false;
}

async function addStock(symbol) {
  if (!symbol || state.watchSymbols.includes(symbol)) {
    elements.input.value = "";
    elements.results.hidden = true;
    return;
  }

  state.watchSymbols.unshift(symbol);
  saveWatchSymbols();
  elements.input.value = "";
  elements.clear.hidden = true;
  elements.results.hidden = true;
  setLoading(true);

  try {
    const stock = await buildStock(symbol);
    state.stocks.unshift(stock);
    render();
  } catch (error) {
    state.watchSymbols = state.watchSymbols.filter((item) => item !== symbol);
    saveWatchSymbols();
    showError(error.message);
  } finally {
    setLoading(false);
  }
}

function removeStock(symbol) {
  state.watchSymbols = state.watchSymbols.filter((item) => item !== symbol);
  state.stocks = state.stocks.filter((item) => item.symbol !== symbol);
  saveWatchSymbols();
  render();
}

function render() {
  const visibleStocks = state.filter === "all"
    ? state.stocks
    : state.stocks.filter((stock) => stock.signal.key === state.filter);

  elements.board.innerHTML = "";
  visibleStocks.forEach((stock) => elements.board.append(createStockCard(stock)));

  const hasAny = state.watchSymbols.length > 0;
  elements.empty.hidden = hasAny || state.loading;
  elements.board.hidden = !hasAny;
  renderSummary();
}

function renderSummary() {
  const counts = { buy: 0, hold: 0, sell: 0 };
  state.stocks.forEach((stock) => counts[stock.signal.key] += 1);
  document.querySelector("#buyCount").textContent = counts.buy;
  document.querySelector("#holdCount").textContent = counts.hold;
  document.querySelector("#sellCount").textContent = counts.sell;
}

function createStockCard(stock) {
  const fragment = elements.template.content.cloneNode(true);
  const card = fragment.querySelector(".stock-card");
  const changePercent = Number.isFinite(stock.change) && Number.isFinite(stock.previousClose) && stock.previousClose !== 0
    ? (stock.change / stock.previousClose) * 100
    : null;

  card.dataset.symbol = stock.symbol;
  card.dataset.signal = stock.signal.key;
  setText(card, ".stock-code", stock.symbol);
  setText(card, ".stock-name", stock.name);
  setText(
    card,
    ".data-date",
    stock.isRealtime
      ? `即時報價 ${formatDate(stock.date)} ${stock.quoteTime}`
      : `收盤資料 ${formatDate(stock.date)}`
  );
  setText(card, ".previous-close", formatPrice(stock.previousClose));
  setText(card, ".previous-date", stock.isRealtime ? "前一交易日" : formatDate(stock.date));
  setText(card, ".stock-price", formatPrice(stock.close));
  setText(card, ".stock-change", `${stock.change > 0 ? "+" : ""}${formatPrice(stock.change)}（${formatPercent(changePercent)}）`);
  setText(
    card,
    ".quote-update-time",
    stock.isRealtime ? `更新 ${stock.quoteTime}` : "等待今日即時報價"
  );
  setText(card, ".current-price-label", stock.isRealtime ? "今日盤價" : "最近收盤");
  card.querySelector(".stock-change").classList.add(stock.change >= 0 ? "positive" : "negative");
  setText(card, ".signal-label", "JASIC 綜合訊號");
  setText(card, ".signal-title", stock.signal.title);
  setText(card, ".signal-score", `技術分數 ${stock.signal.score > 0 ? "+" : ""}${stock.signal.score}`);
  setText(card, ".ma5-value", formatPrice(stock.indicators.ma5));
  setText(card, ".ma20-value", formatPrice(stock.indicators.ma20));
  setText(card, ".rsi-value", Number.isFinite(stock.indicators.rsi) ? stock.indicators.rsi.toFixed(1) : "--");
  setText(card, ".momentum-value", formatPercent(stock.indicators.momentum20));
  setText(card, ".pe-value", Number.isFinite(stock.valuation.pe) ? stock.valuation.pe.toFixed(2) : "--");
  setText(card, ".yield-value", Number.isFinite(stock.valuation.dividendYield) ? `${stock.valuation.dividendYield.toFixed(2)}%` : "--");
  setText(card, ".volume-ratio-value", Number.isFinite(stock.indicators.volumeRatio) ? stock.indicators.volumeRatio.toFixed(2) : "--");

  const reasonList = card.querySelector(".reason-list");
  stock.signal.reasons.forEach((reason) => {
    const item = document.createElement("div");
    item.className = `reason ${reason.type}-reason`;
    item.innerHTML = `<span class="reason-mark">${reason.type === "positive" ? "↑" : reason.type === "negative" ? "↓" : "−"}</span><span>${escapeHtml(reason.text)}</span>`;
    reasonList.append(item);
  });

  const lessons = [
    {
      title: `均線判讀：${stock.indicators.ma5 > stock.indicators.ma20 ? "短線偏強" : "短線偏弱"}`,
      text: "均線適合看趨勢，不適合單獨預測轉折。價格在均線附近反覆穿越時，常代表盤整。"
    },
    {
      title: `RSI 判讀：${getRsiLabel(stock.indicators.rsi)}`,
      text: "RSI 過熱不等於立刻下跌，超賣也不等於立刻反彈；應搭配趨勢與成交量一起觀察。"
    }
  ];

  const lessonContainer = card.querySelector(".indicator-lessons");
  lessons.forEach((lesson) => {
    const item = document.createElement("div");
    item.className = "lesson";
    item.innerHTML = `<h4>${escapeHtml(lesson.title)}</h4><p>${escapeHtml(lesson.text)}</p>`;
    lessonContainer.append(item);
  });

  return fragment;
}

function getRsiLabel(value) {
  if (!Number.isFinite(value)) return "資料不足";
  if (value >= 70) return "偏熱";
  if (value <= 30) return "偏弱／超賣區";
  if (value >= 50) return "偏強";
  return "中性偏弱";
}

function setText(container, selector, value) {
  container.querySelector(selector).textContent = value;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

elements.input.addEventListener("input", () => {
  const query = elements.input.value;
  elements.clear.hidden = !query;
  renderSearchResults(searchCatalog(query), query);
});

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  const matches = searchCatalog(elements.input.value);
  if (matches.length) addStock(matches[0].symbol);
  else renderSearchResults([], elements.input.value);
});

elements.results.addEventListener("click", (event) => {
  const result = event.target.closest("[data-symbol]");
  if (result) addStock(result.dataset.symbol);
});

elements.clear.addEventListener("click", () => {
  elements.input.value = "";
  elements.clear.hidden = true;
  elements.results.hidden = true;
  elements.input.focus();
});

elements.board.addEventListener("click", (event) => {
  const card = event.target.closest(".stock-card");
  if (!card) return;

  if (event.target.closest(".remove-button")) {
    removeStock(card.dataset.symbol);
    return;
  }

  const detailsButton = event.target.closest(".details-button");
  if (detailsButton) {
    const details = card.querySelector(".stock-details");
    const expanded = detailsButton.getAttribute("aria-expanded") === "true";
    detailsButton.setAttribute("aria-expanded", String(!expanded));
    details.hidden = expanded;
  }
});

document.querySelector(".quick-picks").addEventListener("click", (event) => {
  const button = event.target.closest("[data-quick-symbol]");
  if (button) addStock(button.dataset.quickSymbol);
});

elements.refresh.addEventListener("click", () => refreshAll());

elements.filter.addEventListener("change", () => {
  state.filter = elements.filter.value;
  render();
});

document.addEventListener("click", (event) => {
  if (!event.target.closest(".stock-search")) elements.results.hidden = true;
});

refreshAll({ focusSearch: false });
setInterval(() => refreshAll(), AUTO_REFRESH_MS);
