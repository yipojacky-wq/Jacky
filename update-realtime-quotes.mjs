import { mkdir, writeFile } from "node:fs/promises";

const DAILY_URL = "https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL?response=json";
const MIS_URL = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp";
const BATCH_SIZE = 80;

function toNumber(value) {
  const normalized = String(value ?? "").replaceAll(",", "").trim();
  if (!normalized || normalized === "-" || normalized === "--") return null;
  const number = Number(normalized);
  return Number.isFinite(number) ? number : null;
}

function firstPrice(value) {
  return String(value ?? "")
    .split("_")
    .map(toNumber)
    .find((number) => Number.isFinite(number) && number > 0) ?? null;
}

function getTradePrice(quote) {
  return toNumber(quote.z)
    ?? toNumber(quote.pz)
    ?? firstPrice(quote.a)
    ?? firstPrice(quote.b)
    ?? toNumber(quote.o)
    ?? toNumber(quote.y);
}

async function fetchJson(url, headers = {}) {
  const response = await fetch(url, { headers });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}: ${url}`);
  const text = await response.text();
  return JSON.parse(text.trim());
}

async function getListedSymbols() {
  const payload = await fetchJson(DAILY_URL);
  if (payload.stat !== "OK" || !Array.isArray(payload.data)) {
    throw new Error(`Unable to load listed symbols: ${payload.stat}`);
  }
  return payload.data
    .map((row) => row[0])
    .filter((symbol) => /^\d{4}$/.test(symbol));
}

async function getQuoteBatch(symbols) {
  const channels = symbols.map((symbol) => `tse_${symbol}.tw`).join("|");
  const query = new URLSearchParams({
    ex_ch: channels,
    json: "1",
    delay: "0"
  });
  const payload = await fetchJson(`${MIS_URL}?${query}`, {
    Referer: "https://mis.twse.com.tw/stock/index.jsp",
    "User-Agent": "Mozilla/5.0 JASIC-GitHub-Pages-Quote-Updater"
  });
  return Array.isArray(payload.msgArray) ? payload.msgArray : [];
}

function compactQuote(quote) {
  return {
    symbol: quote.c,
    name: String(quote.n || "").replace(/\*+$/, ""),
    price: getTradePrice(quote),
    previousClose: toNumber(quote.y),
    open: toNumber(quote.o),
    high: toNumber(quote.h),
    low: toNumber(quote.l),
    volume: toNumber(quote.v),
    date: quote.d || "",
    time: quote.t || quote["%"] || ""
  };
}

const symbols = await getListedSymbols();
const quotes = [];

for (let index = 0; index < symbols.length; index += BATCH_SIZE) {
  const batch = symbols.slice(index, index + BATCH_SIZE);
  const batchQuotes = await getQuoteBatch(batch);
  quotes.push(...batchQuotes.map(compactQuote));
}

await mkdir("data", { recursive: true });
await writeFile(
  "data/realtime-quotes.json",
  `${JSON.stringify({ generatedAt: new Date().toISOString(), quotes })}\n`,
  "utf8"
);

console.log(`Wrote ${quotes.length} realtime quotes.`);
