:root {
  --bg: #f6f7f9;
  --panel: #ffffff;
  --ink: #1b1f23;
  --muted: #65717b;
  --line: #d8dee4;
  --brand: #1f4d5a;
  --accent: #b4563a;
  --ok: #26734d;
  --shadow: 0 10px 26px rgba(24, 36, 44, 0.08);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: "Segoe UI", "Noto Sans TC", Arial, sans-serif;
  color: var(--ink);
  background: var(--bg);
}

.topbar {
  min-height: 86px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 28px;
  color: #fff;
  background: var(--brand);
}

.topbar h1,
.section-head h2,
.panel h3 {
  margin: 0;
  letter-spacing: 0;
}

.eyebrow {
  margin: 0 0 5px;
  color: inherit;
  opacity: 0.72;
  font-size: 0.78rem;
  text-transform: uppercase;
}

.notice {
  max-width: 320px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 6px;
  font-size: 0.92rem;
  text-align: center;
}

.app-shell {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  min-height: calc(100vh - 86px);
}

.sidebar {
  padding: 18px 12px;
  border-right: 1px solid var(--line);
  background: #edf1f3;
}

.nav-button,
button,
.button-link {
  min-height: 38px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fff;
  color: var(--ink);
  cursor: pointer;
  font: inherit;
}

.nav-button {
  width: 100%;
  margin-bottom: 8px;
  padding: 9px 10px;
  text-align: left;
}

.nav-button.active,
.primary {
  border-color: var(--brand);
  background: var(--brand);
  color: #fff;
}

.content {
  min-width: 0;
  padding: 22px;
}

.view {
  display: none;
}

.view.active {
  display: block;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.panel-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}

.mini-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

button,
.button-link {
  padding: 8px 12px;
  text-decoration: none;
}

.button-link.compact {
  min-height: 30px;
  padding: 5px 8px;
  font-size: 0.82rem;
}

.icon-button {
  width: 40px;
  padding: 0;
  font-size: 1.2rem;
}

.dashboard-grid,
.two-column {
  display: grid;
  grid-template-columns: minmax(320px, 440px) minmax(0, 1fr);
  gap: 16px;
}

.workspace-grid {
  display: grid;
  grid-template-columns: minmax(240px, 0.9fr) minmax(300px, 1fr) minmax(280px, 1fr);
  gap: 16px;
  align-items: start;
}

.panel {
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  box-shadow: var(--shadow);
}

.version-panel {
  margin-top: 14px;
  box-shadow: none;
}

.form-panel {
  display: grid;
  gap: 12px;
}

label {
  display: grid;
  gap: 6px;
  color: var(--muted);
  font-size: 0.92rem;
}

input,
textarea,
select {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px;
  color: var(--ink);
  background: #fff;
  font: inherit;
}

textarea {
  resize: vertical;
}

.case-list,
.doc-list,
.result-stack {
  display: grid;
  gap: 10px;
}

.case-item {
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbfcfd;
  cursor: pointer;
}

.case-item.active {
  border-color: var(--brand);
  box-shadow: inset 4px 0 0 var(--brand);
}

.case-meta,
.doc-list {
  color: var(--muted);
  font-size: 0.88rem;
}

.status-pill {
  display: inline-flex;
  width: fit-content;
  margin-top: 8px;
  padding: 4px 8px;
  border-radius: 999px;
  color: #fff;
  background: var(--accent);
  font-size: 0.78rem;
}

.text-preview,
.code-editor {
  width: 100%;
  max-height: 68vh;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.55;
}

.text-preview {
  margin: 0;
  color: #26323a;
  font-family: "Consolas", "Noto Sans Mono CJK TC", monospace;
  font-size: 0.9rem;
}

.code-editor {
  min-height: 420px;
  font-family: "Consolas", "Noto Sans Mono CJK TC", monospace;
}

.result-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
  background: #fbfcfd;
}

.result-card h4 {
  margin: 0 0 8px;
}

.result-card pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.82rem;
}

.checkline {
  display: flex;
  grid-template-columns: none;
  align-items: center;
  gap: 8px;
}

.checkline input {
  width: auto;
}

.toast {
  position: fixed;
  right: 18px;
  bottom: 18px;
  max-width: 360px;
  padding: 12px 14px;
  border-radius: 8px;
  color: #fff;
  background: var(--ok);
  opacity: 0;
  transform: translateY(8px);
  transition: 160ms ease;
  pointer-events: none;
}

.toast.show {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 980px) {
  .app-shell,
  .dashboard-grid,
  .two-column,
  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: flex;
    overflow-x: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .nav-button {
    min-width: 170px;
    text-align: center;
  }
}

@media (max-width: 640px) {
  .topbar,
  .section-head {
    align-items: stretch;
    flex-direction: column;
  }

  .content {
    padding: 14px;
  }

  .actions {
    width: 100%;
  }

  .actions button,
  .actions .button-link {
    flex: 1 1 150px;
  }
}
