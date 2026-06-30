# 省額度模式

手機或免費額度環境請優先使用「省額度一鍵補全」。

此模式只呼叫一次 AI，會同時回填：

- Engineering Definition
- Disclosure Completion
- Progressive Elaboration
- Embodiment Expansion
- Completed Disclosure Draft

目的：

- 降低 Gemini / OpenRouter 免費額度被多次呼叫消耗的速度
- 降低 `HTTP Error 429: Too Many Requests` 發生機率
- 讓手機端仍可用同一個 Render / 主機連結操作，不需要在手機貼 API Key

若 AI provider 因免費額度或流量限制失敗，系統仍會產生可人工編輯的本機 fallback，並在揭露書中標示 `AI Gateway Warning`。

API：

```text
POST /cases/{case_id}/run-low-quota-completion
```

一般建議流程：

1. 建立案件
2. 貼上文字、上傳 Word/PDF/TXT，或手機拍照 OCR
3. 點「省額度一鍵補全」
4. 人工修改「完整可撰寫揭露書」
5. 匯出 Markdown 或 Word docx

## 多頁拍照 OCR

手機端可在「手機多頁拍照 OCR」選擇多張圖片。系統會依照選取順序逐頁 OCR，並以：

```text
【OCR 第 1 頁：檔名】
...

【OCR 第 2 頁：檔名】
...
```

寫入原始揭露內容。

注意：每一頁照片都需要一次 OCR 呼叫，因此大量頁面仍可能消耗 Gemini 額度。建議先用多頁 OCR 整理原文，再用「省額度一鍵補全」產生完整揭露書。
