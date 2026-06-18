# JASIC 台股觀測學習看板

這是一個可部署到 GitHub Pages 的純前端台股觀測 App。

## 主要功能

- 輸入上市股票名稱或代號，自動搜尋並加入觀察
- 使用臺灣證券交易所公開資料更新行情
- 自動計算 MA5、MA20、RSI 14、20 日漲跌與成交量比
- 將結果整理為「買進觀察」、「可持有」、「拋售警示」
- 每檔股票可展開查看判讀理由及技術指標教學
- 觀察清單儲存在使用者自己的瀏覽器
- 首次開啟預設觀察國巨（2327）、南亞科（2408）、聯電（2303）
- 交易日上午由 GitHub Actions 約每 5 分鐘抓取證交所 MIS 即時報價
- 同步顯示證交所「臺灣加權指數」與期交所「臺指期夜盤」近月合約
- 臺指期夜盤明確標示為期貨點位，不與現貨指數混用
- App 每 5 分鐘檢查最新報價，並顯示實際最後報價時刻

## 資料來源

- 臺灣證券交易所當日成交資訊
- 臺灣證券交易所個股日成交資訊
- 臺灣證券交易所本益比、殖利率及股價淨值比

目前版本支援臺灣證券交易所上市股票。盤中價格取自證交所 MIS 即時報價；技術指標仍以證交所日線搭配最新盤中價格計算。

## 部署

將以下檔案上傳至 GitHub Repository 根目錄：

- `index.html`
- `styles.css`
- `app.js`
- `README.md`
- `manifest.webmanifest`
- `assets/jasic-icon.png`
- `assets/jasic-180.png`
- `assets/jasic-192.png`
- `assets/jasic-512.png`

由於即時報價需要 GitHub Actions 產生同網域資料檔，請到：

`Settings` → `Pages` → `Build and deployment` → `Source` 選擇 `GitHub Actions`

工作流程位於 `.github/workflows/deploy-pages.yml`，會在：

- `main` 分支更新時部署
- 週一至週五臺灣時間約 09:00–14:55，每 5 分鐘更新一次
- 在 Actions 頁面手動執行時部署

GitHub 的排程服務可能延遲數分鐘，因此畫面以「最後更新時刻」為準。

## 免責聲明

本工具僅供學習與建立觀察紀律，不構成投資建議。技術指標來自歷史價格，不能保證未來績效。
