<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Disclosure Completion AI - 上傳測試</title>
    <style>
      * { box-sizing: border-box; }
      body { margin: 0; font-family: system-ui, "Noto Sans TC", sans-serif; color: #172026; background: #f6f7f9; }
      header { padding: 18px 22px; color: #fff; background: #1f4d5a; }
      main { max-width: 980px; margin: 0 auto; padding: 18px; display: grid; gap: 14px; }
      section { background: #fff; border: 1px solid #d8dee4; border-radius: 8px; padding: 16px; }
      label { display: grid; gap: 6px; margin: 10px 0; color: #53616b; }
      input, textarea, button { font: inherit; }
      input, textarea { width: 100%; border: 1px solid #d8dee4; border-radius: 6px; padding: 10px; }
      textarea { min-height: 360px; line-height: 1.55; }
      button { border: 0; border-radius: 6px; padding: 10px 14px; color: #fff; background: #1f4d5a; }
      .status { color: #53616b; }
      .error { color: #9b2f17; white-space: pre-wrap; }
      .row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
    </style>
  </head>
  <body>
    <header>
      <div>Disclosure Completion AI</div>
      <h1>上傳並擷取文字測試頁</h1>
    </header>
    <main>
      <section>
        <label>案件名稱
          <input id="caseTitle" placeholder="空白時會使用檔名" />
        </label>
        <label>選擇檔案
          <input id="fileInput" type="file" accept=".txt,.md,.csv,.json,.docx,.pdf" />
        </label>
        <div class="row">
          <button id="uploadButton" type="button">上傳並擷取文字</button>
          <a href="/" id="backLink">返回主程式</a>
        </div>
        <p id="status" class="status">支援 txt、md、docx、可抽取文字的 pdf。</p>
        <div id="error" class="error"></div>
      </section>
      <section>
        <h2>擷取結果</h2>
        <textarea id="resultText" placeholder="擷取出的文字會出現在這裡"></textarea>
      </section>
    </main>
    <script>
      const $ = (id) => document.getElementById(id);

      async function api(path, options = {}) {
        const response = await fetch(path, {
          headers: options.body instanceof FormData ? {} : { "Content-Type": "application/json" },
          ...options,
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
      }

      function readableError(error) {
        const raw = error?.message || String(error);
        try {
          const parsed = JSON.parse(raw);
          return parsed.detail || raw;
        } catch {
          return raw;
        }
      }

      $("uploadButton").onclick = async () => {
        const file = $("fileInput").files[0];
        $("error").textContent = "";
        if (!file) {
          $("status").textContent = "請先選擇檔案。";
          return;
        }
        const title = $("caseTitle").value.trim() || file.name.replace(/\.[^.]+$/, "") || "未命名案件";
        $("uploadButton").disabled = true;
        $("uploadButton").textContent = "處理中...";
        try {
          $("status").textContent = `正在建立案件：${title}`;
          const created = await api("/cases", {
            method: "POST",
            body: JSON.stringify({
              case_title: title,
              client_name: "",
              inventors: [],
              technical_field: "",
              transcript_or_disclosure_text: "",
            }),
          });
          $("status").textContent = `正在上傳並解析：${file.name}`;
          const formData = new FormData();
          formData.append("file", file);
          const updated = await api(`/cases/${created.case_id}/upload`, {
            method: "POST",
            body: formData,
          });
          $("resultText").value = updated.transcript_or_disclosure_text || "";
          $("status").textContent = `完成。已建立案件並擷取文字：${file.name}`;
        } catch (error) {
          $("status").textContent = "上傳或解析失敗。";
          $("error").textContent = readableError(error);
        } finally {
          $("uploadButton").disabled = false;
          $("uploadButton").textContent = "上傳並擷取文字";
        }
      };
    </script>
  </body>
</html>
