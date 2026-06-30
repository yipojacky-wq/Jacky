# Disclosure Completion AI MVP

Patent Engineering Framework Phase 1 MVP。

本工具不是 Claim Generator，也不是完整專利說明書生成器。目標是將原始專利揭露書、發明人口述逐字稿、技術說明文件或會議記錄，整理補足為一份「可供專利工程師撰寫專利說明書使用的完整揭露書」。

所有 AI 輸出均為初稿，需由專利工程師確認。

## 功能

- 建立案件與保存狀態
- 貼上原始揭露內容
- 上傳 `.txt`、`.md`、`.docx`、可抽取文字的 `.pdf`
- 手機拍照或上傳圖片後，以 Gemini Vision 進行 OCR 文字辨識
- AI 產生 Engineering Definition
- AI 產生 Disclosure Completion
- AI 產生 Progressive Elaboration
- AI 產生 Embodiment Expansion
- AI 產生 Completed Disclosure Draft
- 人工編輯 Engineering Definition 與完整揭露書
- 保存揭露書版本
- 匯出 Markdown
- 匯出 Word docx
- Responsive Web App / PWA，可由手機瀏覽器開啟同一服務網址

## 重要限制

本 MVP 不做：

- Claim 生成
- 完整專利說明書生成
- 專利檢索
- FTO
- 圖式生成
- 多 AI Agent 協作

## 啟動

Windows 使用者可直接執行：

```bat
run-windows.bat
```

服務網址：

```text
http://127.0.0.1:8010
```

## API Key 設定

正式 AI 推論需要 API Key。Demo 模式不需要 API Key，但只會產生本機 fallback 內容。

### Google Gemini

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=你的 Gemini API Key
GEMINI_MODEL=gemini-2.5-flash
APP_DEMO_MODE=false
```

### OpenRouter

```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=你的 OpenRouter API Key
OPENROUTER_MODEL=openrouter/free
APP_DEMO_MODE=false
```

### OpenAI

```env
AI_PROVIDER=openai
OPENAI_API_KEY=你的 OpenAI API Key
OPENAI_MODEL=gpt-4.1-mini
APP_DEMO_MODE=false
```

## 前端操作流程

1. Dashboard 建立案件
2. 在 Case Detail 貼上原始揭露內容或上傳檔案
3. 進入「可撰寫揭露書生成」
4. 點選「一鍵補全」或分別執行各 AI 模組
5. 檢查右側完整揭露書預覽
6. 進入 Completed Disclosure Draft 人工修改
7. 儲存揭露書或保存版本
8. 匯出 Markdown / Word docx

## 後端 API

案件 API：

- `POST /cases`
- `GET /cases`
- `GET /cases/{case_id}`
- `PUT /cases/{case_id}`
- `DELETE /cases/{case_id}`
- `DELETE /cases`

上傳：

- `POST /cases/{case_id}/upload`

Completion AI：

- `POST /cases/{case_id}/engineering-definition`
- `POST /cases/{case_id}/complete-disclosure`
- `POST /cases/{case_id}/progressive-elaboration-disclosure`
- `POST /cases/{case_id}/embodiment-expansion`
- `POST /cases/{case_id}/generate-completed-disclosure-draft`
- `POST /cases/{case_id}/run-full-completion`
- `POST /cases/{case_id}/save-draft-version`
- `POST /cases/{case_id}/clear-completion`

匯出：

- `GET /cases/{case_id}/export/completed-disclosure/markdown`
- `GET /cases/{case_id}/export/completed-disclosure/docx`

## 狀態

- Draft
- Uploaded
- Engineering Defined
- Disclosure Completed
- Engineer Edited
- Ready for Specification Drafting
- Exported

## Demo

- Demo 原始揭露書：`demo/demo_raw_disclosure.md`
- Demo Engineering Definition：`demo/demo_engineering_definition.json`
- Demo Completed Disclosure Draft：`demo/demo_completed_disclosure_draft.md`

## 手機端使用

手機與主機在同一 Wi-Fi 時：

1. 主機執行 `run-windows.bat`
2. 手機或其他主機開啟 `http://主機IP:8010`
3. 本次已提供連結檔：`outputs/Open-DisclosureCompletionAI-Host.url`

手機與主機不在同一 Wi-Fi 時：

- 使用 `outputs/DisclosureCompletionAI-Mobile-Standalone.html`
- 該單檔會直接由手機瀏覽器呼叫 Google Gemini
- API Key 會保存在手機瀏覽器本機儲存空間

若要把主機版分享給外部網路的其他人：

1. 先執行 `run-windows.bat`
2. 安裝 Cloudflare Tunnel 的 `cloudflared`
3. 執行 `run-public-tunnel.bat`
4. 將畫面中產生的 `https://*.trycloudflare.com` 連結分享出去

## 專案結構

```text
app/
  main.py
  models.py
  exporters.py
  services/
    ai_completion.py
    ai_gateway.py
    document_text.py
    prompts.py
static/
  index.html
  assets/app.js
  assets/app.css
demo/
outputs/
```
