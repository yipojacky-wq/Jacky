# GitHub 部署方式：手機免 API Key 直接開連結

本專案可以採用 GitHub 作為程式碼來源，再部署到 Render / Railway / Fly.io 等雲端後端。  
手機只開雲端網址，不需要輸入 API Key。API Key 放在雲端環境變數。

## 為什麼不能只用 GitHub Pages

GitHub Pages 只能放靜態網頁，不能安全保存 API Key，也不能執行 FastAPI 後端。

如果把 API Key 寫進手機網頁或 GitHub Pages，任何人都能看到 Key。  
所以正式使用請採用：

```text
GitHub Repo -> 雲端後端服務 -> 手機瀏覽器開網址
```

## 建議架構

```text
手機 / 電腦瀏覽器
        ↓
雲端網址，例如 https://disclosure-completion-ai.onrender.com
        ↓
FastAPI 後端
        ↓
Gemini / OpenAI / OpenRouter API Key（只存在雲端環境變數）
```

## 上傳到 GitHub

1. 到 GitHub 建立新 Repository，例如：
   `disclosure-completion-ai`
2. 上傳本專案資料夾內容。
3. 不要上傳 `.env`、`.venv`、`outputs/server.log`。
4. `.env.example` 可以上傳。

如果你的電腦沒有 Git，可以直接用 GitHub 網頁：

1. 點 `Add file`
2. 點 `Upload files`
3. 將專案檔案拖進去
4. Commit changes

## Render 部署方式

1. 到 Render 建立帳號。
2. New -> Web Service。
3. 選擇 GitHub Repository。
4. Build Command：

```bash
pip install -r requirements.txt
```

5. Start Command：

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

6. Environment Variables 設定：

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=你的 Gemini API Key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
APP_DEMO_MODE=false
APP_STORAGE_PATH=/tmp/disclosure-completion-cases.json
```

本 OCR 版本的手機拍照辨識使用 Gemini Vision，因此請優先設定：

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=你的 Gemini API Key
GEMINI_MODEL=gemini-2.5-flash
APP_DEMO_MODE=false
APP_STORAGE_PATH=/tmp/disclosure-completion-cases.json
```

7. Deploy。
8. Render 會給你一個網址，例如：

```text
https://disclosure-completion-ai.onrender.com
```

手機直接開這個網址即可操作，不需要輸入 API Key。

## OpenRouter 或 OpenAI

若改用 OpenRouter：

```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=你的 OpenRouter Key
OPENROUTER_MODEL=你要使用的模型
APP_DEMO_MODE=false
```

若改用 OpenAI：

```env
AI_PROVIDER=openai
OPENAI_API_KEY=你的 OpenAI Key
OPENAI_MODEL=gpt-4.1-mini
APP_DEMO_MODE=false
```

## 注意

- Render 免費服務可能會休眠，第一次開啟會比較慢。
- `/tmp/disclosure-completion-cases.json` 適合 MVP 測試，不保證長期保存。
- 若要正式保存案件資料，下一階段建議改 PostgreSQL 或雲端資料庫。
