const statuses = [
  "Draft",
  "Uploaded",
  "Engineering Defined",
  "Disclosure Completed",
  "Engineer Edited",
  "Ready for Specification Drafting",
  "Exported",
];

let cases = [];
let currentCase = null;

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function toast(message) {
  const node = $("#toast");
  node.textContent = message;
  node.classList.add("show");
  setTimeout(() => node.classList.remove("show"), 2600);
}

async function api(path, options = {}) {
  const headers = options.headers || (options.body instanceof FormData ? {} : { "Content-Type": "application/json" });
  const response = await fetch(path, {
    headers,
    ...options,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function showView(id) {
  $$(".view").forEach((view) => view.classList.toggle("active", view.id === id));
  $$(".nav-button").forEach((button) => button.classList.toggle("active", button.dataset.view === id));
}

function renderCaseList() {
  const list = $("#caseList");
  if (!cases.length) {
    list.innerHTML = `<p class="case-meta">尚無案件。請先新增案件或貼上原始揭露內容。</p>`;
    return;
  }
  list.innerHTML = cases
    .map(
      (item) => `
      <article class="case-item ${currentCase?.case_id === item.case_id ? "active" : ""}" data-case-id="${item.case_id}">
        <strong>${escapeHtml(item.case_title)}</strong>
        <div class="case-meta">${escapeHtml(item.client_name || "未填客戶")} · ${escapeHtml(item.technical_field || "未填技術領域")}</div>
        <span class="status-pill">${escapeHtml(item.status)}</span>
      </article>
    `,
    )
    .join("");
  $$(".case-item").forEach((item) => {
    item.addEventListener("click", async () => {
      currentCase = await api(`/cases/${item.dataset.caseId}`);
      renderAll();
      showView("detail");
    });
  });
}

function renderCaseForm() {
  const form = $("#caseForm");
  form.elements.status.innerHTML = statuses.map((status) => `<option>${status}</option>`).join("");
  if (!currentCase) {
    $("#detailTitle").textContent = "尚未選擇案件";
    $("#saveCase").textContent = "儲存案件";
    form.reset();
    $("#uploadStatus").textContent = "可直接上傳檔案擷取文字；擷取後可按「儲存案件」建立案件。";
    $("#sourceDocs").innerHTML = `<p>尚未上傳檔案。</p>`;
    return;
  }
  $("#saveCase").textContent = "儲存案件";
  $("#detailTitle").textContent = currentCase.case_title;
  form.elements.case_title.value = currentCase.case_title || "";
  form.elements.client_name.value = currentCase.client_name || "";
  form.elements.inventors.value = (currentCase.inventors || []).join(", ");
  form.elements.technical_field.value = currentCase.technical_field || "";
  form.elements.status.value = currentCase.status || "Draft";
  form.elements.transcript_or_disclosure_text.value = currentCase.transcript_or_disclosure_text || "";
  $("#sourceDocs").innerHTML =
    (currentCase.source_documents || [])
      .map((doc) => `<p>${escapeHtml(doc.filename)} · ${escapeHtml(doc.uploaded_at)}</p>`)
      .join("") || `<p>尚未上傳檔案。</p>`;
}

function renderWorkspace() {
  $("#sourcePreview").textContent = currentCase?.transcript_or_disclosure_text || "尚未輸入原始揭露內容。";
  $("#draftPreview").textContent = currentCase?.completed_disclosure_draft || "尚未產生完整揭露書。";
  const sections = [
    ["工程定義", currentCase?.engineering_definition],
    ["揭露補全", currentCase?.disclosure_completion],
    ["進步性鋪陳", currentCase?.progressive_elaboration_disclosure],
    ["實施例擴充", currentCase?.embodiment_expansion],
  ];
  $("#moduleResults").innerHTML = sections
    .map(([title, data]) => `<article class="result-card"><h4>${title}</h4><pre>${escapeHtml(JSON.stringify(data || {}, null, 2))}</pre></article>`)
    .join("");
}

function renderEditors() {
  $("#definitionEditor").value = JSON.stringify(currentCase?.engineering_definition || {}, null, 2);
  $("#definitionConfirmed").checked = Boolean(currentCase?.engineering_definition_confirmed);
  $("#draftEditor").value = currentCase?.completed_disclosure_draft || "";
  $("#draftVersions").innerHTML =
    (currentCase?.draft_versions || [])
      .slice()
      .reverse()
      .map((version) => `<p>${escapeHtml(version.saved_at)} · ${escapeHtml(version.title || "未命名版本")}</p>`)
      .join("") || `<p>尚未保存版本。</p>`;

  if (currentCase) {
    const md = `/cases/${currentCase.case_id}/export/completed-disclosure/markdown`;
    const docx = `/cases/${currentCase.case_id}/export/completed-disclosure/docx`;
    $("#exportMarkdown").href = md;
    $("#exportDocx").href = docx;
    $("#workspaceExportMarkdown").href = md;
    $("#workspaceExportDocx").href = docx;
  }
}

function renderAll() {
  renderCaseList();
  renderCaseForm();
  renderWorkspace();
  renderEditors();
}

async function loadCases() {
  cases = await api("/cases");
  if (!currentCase && cases.length) {
    currentCase = await api(`/cases/${cases[0].case_id}`);
  } else if (currentCase && cases.some((item) => item.case_id === currentCase.case_id)) {
    currentCase = await api(`/cases/${currentCase.case_id}`);
  } else if (!cases.length) {
    currentCase = null;
  }
  renderAll();
}

async function removeOldServiceWorkers() {
  if (!("serviceWorker" in navigator)) return;
  const registrations = await navigator.serviceWorker.getRegistrations();
  await Promise.all(registrations.map((registration) => registration.unregister()));
}

async function saveCase(updates) {
  if (!currentCase) {
    const payload = { ...updates };
    if (!payload.case_title?.trim()) payload.case_title = "未命名案件";
    currentCase = await api("/cases", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    await loadCases();
    toast("案件已建立並儲存");
    return;
  }
  currentCase = await api(`/cases/${currentCase.case_id}`, {
    method: "PUT",
    body: JSON.stringify(updates),
  });
  await loadCases();
  toast("已儲存");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function detailFormPayload() {
  const form = $("#caseForm");
  return {
    case_title: form.elements.case_title.value,
    client_name: form.elements.client_name.value,
    inventors: form.elements.inventors.value.split(",").map((item) => item.trim()).filter(Boolean),
    technical_field: form.elements.technical_field.value,
    transcript_or_disclosure_text: form.elements.transcript_or_disclosure_text.value,
  };
}

$$(".nav-button").forEach((button) => button.addEventListener("click", () => showView(button.dataset.view)));

$("#refreshCases").addEventListener("click", loadCases);

$("#clearAllCases").addEventListener("click", async () => {
  try {
    await api("/cases/clear-all", { method: "POST" });
    cases = [];
    currentCase = null;
    renderAll();
    showView("dashboard");
    toast("全部案件已清空");
  } catch (error) {
    toast(`清空失敗：${readableError(error)}`);
  }
});

$("#newCaseForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = {
    case_title: form.elements.case_title.value,
    client_name: form.elements.client_name.value,
    inventors: form.elements.inventors.value.split(",").map((item) => item.trim()).filter(Boolean),
    technical_field: form.elements.technical_field.value,
    transcript_or_disclosure_text: form.elements.transcript_or_disclosure_text.value,
  };
  currentCase = await api("/cases", { method: "POST", body: JSON.stringify(payload) });
  form.reset();
  await loadCases();
  showView("detail");
  toast("案件已建立");
});

$("#saveCase").addEventListener("click", async () => {
  const payload = detailFormPayload();
  if (currentCase) payload.status = $("#caseForm").elements.status.value;
  await saveCase(payload);
});

$("#uploadButton").addEventListener("click", async () => {
  const file = $("#uploadFile").files[0];
  await extractFileToDisclosure(file, $("#uploadButton"), "上傳並擷取文字", "請選擇 txt、docx、pdf 或文字檔案");
  if (file) $("#uploadFile").value = "";
});

$("#photoOcrButton").addEventListener("click", async () => {
  const files = Array.from($("#photoFile").files || []);
  await extractPhotoPagesToDisclosure(files, $("#photoOcrButton"), "多頁拍照 OCR 擷取文字");
  if (files.length) $("#photoFile").value = "";
});

async function extractPhotoPagesToDisclosure(files, button, originalLabel) {
  const status = $("#uploadStatus");
  if (!files.length) {
    status.textContent = "尚未選擇照片。";
    return toast("請先拍照或選擇一張以上圖片");
  }
  button.disabled = true;
  button.textContent = "多頁 OCR 中...";
  const extractedPages = [];
  try {
    for (const [index, file] of files.entries()) {
      status.textContent = `正在 OCR 第 ${index + 1} / ${files.length} 頁：${file.name}`;
      const formData = new FormData();
      formData.append("file", file);
      const extracted = await api("/extract-text", { method: "POST", body: formData });
      extractedPages.push(`【OCR 第 ${index + 1} 頁：${extracted.filename || file.name}】\n${extracted.text.trim()}`);
    }

    const form = $("#caseForm");
    form.elements.transcript_or_disclosure_text.value = [
      form.elements.transcript_or_disclosure_text.value.trim(),
      extractedPages.join("\n\n"),
    ].filter(Boolean).join("\n\n");

    if (currentCase) {
      currentCase = await api(`/cases/${currentCase.case_id}`, {
        method: "PUT",
        body: JSON.stringify({
          ...detailFormPayload(),
          status: "Uploaded",
        }),
      });
      await loadCases();
      showView("detail");
      status.textContent = `已完成 ${files.length} 頁 OCR，並寫入揭露內容。`;
    } else {
      status.textContent = `已完成 ${files.length} 頁 OCR，請在 Dashboard 建立案件後保存。`;
    }
    toast(`多頁 OCR 完成：${files.length} 頁`);
  } catch (error) {
    status.textContent = `多頁 OCR 失敗：${readableError(error)}`;
    toast(readableError(error));
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

async function extractFileToDisclosure(file, button, originalLabel, emptyMessage) {
  const status = $("#uploadStatus");
  if (!file) {
    status.textContent = "尚未選擇檔案。";
    return toast(emptyMessage);
  }
  button.disabled = true;
  button.textContent = "處理中...";
  status.textContent = `正在上傳並解析：${file.name}`;
  try {
    const formData = new FormData();
    formData.append("file", file);
    const extracted = await api("/extract-text", { method: "POST", body: formData });
    const form = $("#caseForm");
    form.elements.transcript_or_disclosure_text.value = [
      form.elements.transcript_or_disclosure_text.value.trim(),
      extracted.text.trim(),
    ].filter(Boolean).join("\n\n");

    if (currentCase) {
      currentCase = await api(`/cases/${currentCase.case_id}`, {
        method: "PUT",
        body: JSON.stringify({
          ...detailFormPayload(),
          status: "Uploaded",
        }),
      });
      await loadCases();
      showView("detail");
      status.textContent = `已擷取文字並儲存至案件：${file.name}`;
    } else {
      status.textContent = `已擷取文字並放入輸入區：${file.name}。請按「儲存案件」或到 Dashboard 建立案件。`;
    }
    toast("檔案已上傳並擷取文字");
  } catch (error) {
    status.textContent = `上傳失敗：${readableError(error)}`;
    toast(readableError(error));
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
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

$$("[data-ai]").forEach((button) => {
  const originalLabel = button.textContent;
  button.addEventListener("click", async () => {
    if (!currentCase) return toast("請先選擇案件");
    button.disabled = true;
    button.textContent = "執行中...";
    try {
      currentCase = await api(`/cases/${currentCase.case_id}/${button.dataset.ai}`, { method: "POST" });
      await loadCases();
      toast("AI 補全完成");
    } catch (error) {
      toast(error.message);
    } finally {
      button.disabled = false;
      button.textContent = originalLabel;
    }
  });
});

$("#saveDefinition").addEventListener("click", async () => {
  let parsed;
  try {
    parsed = JSON.parse($("#definitionEditor").value || "{}");
  } catch {
    return toast("工程定義 JSON 格式不正確");
  }
  await saveCase({
    engineering_definition: parsed,
    engineering_definition_confirmed: $("#definitionConfirmed").checked,
    status: $("#definitionConfirmed").checked ? "Engineer Edited" : currentCase.status,
  });
});

$("#saveDraft").addEventListener("click", async () => {
  await saveCase({
    completed_disclosure_draft: $("#draftEditor").value,
    status: "Engineer Edited",
  });
});

$("#saveDraftVersion").addEventListener("click", async () => {
  if (!currentCase) return toast("請先選擇案件");
  await saveCase({
    completed_disclosure_draft: $("#draftEditor").value,
    status: "Engineer Edited",
  });
  currentCase = await api(`/cases/${currentCase.case_id}/save-draft-version`, { method: "POST" });
  await loadCases();
  toast("已保存版本");
});

removeOldServiceWorkers()
  .catch(() => {})
  .finally(() => loadCases().catch((error) => toast(error.message)));
