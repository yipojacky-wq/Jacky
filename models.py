from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from .exporters import markdown_to_docx_bytes
from .models import CaseCreate, CaseStatus, CaseUpdate, DraftVersion, SourceDocument
from .services.ai_completion import (
    generate_completed_disclosure_draft,
    generate_disclosure_completion,
    generate_embodiment_expansion,
    generate_engineering_definition,
    generate_progressive_elaboration_for_disclosure,
)
from .services.document_text import extract_upload_text
from .storage import make_store

load_dotenv(override=True)

app = FastAPI(title="Disclosure Completion AI MVP", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
store = make_store()


@app.middleware("http")
async def no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def get_or_404(case_id: str):
    try:
        return store.get_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")


@app.post("/cases")
def create_case(payload: CaseCreate):
    return store.create_case(payload)


@app.get("/cases")
def list_cases():
    return store.list_cases()


@app.get("/cases/{case_id}")
def get_case(case_id: str):
    return get_or_404(case_id)


@app.put("/cases/{case_id}")
def update_case(case_id: str, payload: CaseUpdate):
    try:
        return store.update_case(case_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")


@app.delete("/cases/{case_id}")
def delete_case(case_id: str):
    try:
        store.delete_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"ok": True}


@app.delete("/cases")
def delete_all_cases():
    store.delete_all_cases()
    return {"ok": True}


@app.post("/cases/clear-all")
def clear_all_cases():
    store.delete_all_cases()
    return {"ok": True}


@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        text = extract_upload_text(file.filename or "upload.txt", file.content_type or "application/octet-stream", raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "filename": file.filename or "upload.txt",
        "content_type": file.content_type or "text/plain",
        "text": text,
    }


@app.post("/cases/{case_id}/upload")
async def upload_disclosure(case_id: str, file: UploadFile = File(...)):
    case = get_or_404(case_id)
    raw = await file.read()
    try:
        text = extract_upload_text(file.filename or "upload.txt", file.content_type or "application/octet-stream", raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    documents = list(case.source_documents)
    documents.append(
        SourceDocument(
            filename=file.filename or "upload.txt",
            content_type=file.content_type or "text/plain",
            text=text,
        )
    )
    merged_text = (case.transcript_or_disclosure_text + "\n\n" + text).strip()
    return store.update_case(
        case_id,
        {
            "source_documents": [doc.model_dump() for doc in documents],
            "transcript_or_disclosure_text": merged_text,
            "status": CaseStatus.uploaded,
        },
    )


@app.post("/cases/{case_id}/engineering-definition")
def engineering_definition(case_id: str):
    case = get_or_404(case_id)
    result = generate_engineering_definition(case.transcript_or_disclosure_text)
    return store.update_case(
        case_id,
        {
            "engineering_definition": result,
            "original_solution": result.get("original_solution", ""),
            "engineering_boundary": result.get("engineering_boundary", ""),
            "project_scope": result.get("project_scope", ""),
            "status": CaseStatus.engineering_defined,
        },
    )


@app.post("/cases/{case_id}/complete-disclosure")
def complete_disclosure(case_id: str):
    case = get_or_404(case_id)
    definition = case.engineering_definition or generate_engineering_definition(case.transcript_or_disclosure_text)
    if not case.engineering_definition:
        case = store.update_case(case_id, {"engineering_definition": definition, "status": CaseStatus.engineering_defined})
    result = generate_disclosure_completion(case.transcript_or_disclosure_text, definition)
    return store.update_case(case_id, {"disclosure_completion": result, "status": CaseStatus.disclosure_completed})


@app.post("/cases/{case_id}/progressive-elaboration-disclosure")
def progressive_elaboration_disclosure(case_id: str):
    case = get_or_404(case_id)
    result = generate_progressive_elaboration_for_disclosure(case.model_dump(mode="json"))
    return store.update_case(case_id, {"progressive_elaboration_disclosure": result, "status": CaseStatus.disclosure_completed})


@app.post("/cases/{case_id}/embodiment-expansion")
def embodiment_expansion(case_id: str):
    case = get_or_404(case_id)
    result = generate_embodiment_expansion(case.model_dump(mode="json"))
    return store.update_case(case_id, {"embodiment_expansion": result, "status": CaseStatus.disclosure_completed})


@app.post("/cases/{case_id}/generate-completed-disclosure-draft")
def completed_disclosure_draft(case_id: str):
    case = get_or_404(case_id)
    draft = generate_completed_disclosure_draft(case)
    return store.update_case(
        case_id,
        {
            "completed_disclosure_draft": draft,
            "status": CaseStatus.disclosure_completed,
        },
    )


@app.post("/cases/{case_id}/run-full-completion")
def run_full_completion(case_id: str):
    case = get_or_404(case_id)
    definition = generate_engineering_definition(case.transcript_or_disclosure_text)
    case = store.update_case(
        case_id,
        {
            "engineering_definition": definition,
            "original_solution": definition.get("original_solution", ""),
            "engineering_boundary": definition.get("engineering_boundary", ""),
            "project_scope": definition.get("project_scope", ""),
            "status": CaseStatus.engineering_defined,
        },
    )
    completion = generate_disclosure_completion(case.transcript_or_disclosure_text, definition)
    case = store.update_case(case_id, {"disclosure_completion": completion, "status": CaseStatus.disclosure_completed})
    elaboration = generate_progressive_elaboration_for_disclosure(case.model_dump(mode="json"))
    case = store.update_case(case_id, {"progressive_elaboration_disclosure": elaboration})
    embodiment = generate_embodiment_expansion(case.model_dump(mode="json"))
    case = store.update_case(case_id, {"embodiment_expansion": embodiment})
    draft = generate_completed_disclosure_draft(case)
    return store.update_case(
        case_id,
        {
            "completed_disclosure_draft": draft,
            "status": CaseStatus.disclosure_completed,
        },
    )


@app.post("/cases/{case_id}/save-draft-version")
def save_draft_version(case_id: str):
    case = get_or_404(case_id)
    content = case.completed_disclosure_draft
    if not content:
        raise HTTPException(status_code=400, detail="No completed disclosure draft to save")
    versions = list(case.draft_versions)
    versions.append(DraftVersion(title=case.case_title, content=content))
    return store.update_case(
        case_id,
        {
            "draft_versions": [version.model_dump() for version in versions],
            "status": CaseStatus.engineer_edited,
        },
    )


@app.post("/cases/{case_id}/clear-completion")
def clear_completion(case_id: str):
    get_or_404(case_id)
    return store.update_case(
        case_id,
        {
            "engineering_definition": {},
            "disclosure_completion": {},
            "progressive_elaboration_disclosure": {},
            "embodiment_expansion": {},
            "completed_disclosure_draft": "",
            "engineering_definition_confirmed": False,
            "completed_disclosure_confirmed": False,
            "status": CaseStatus.uploaded,
        },
    )


def _completed_markdown(case_id: str) -> tuple[str, str]:
    case = get_or_404(case_id)
    markdown = case.completed_disclosure_draft or generate_completed_disclosure_draft(case)
    return markdown, case.case_title or case.case_id


def _safe_download_headers(filename: str, fallback: str) -> dict[str, str]:
    safe_filename = filename.replace("/", "_").replace("\\", "_").replace("\r", "").replace("\n", "")
    ascii_fallback = "".join(char for char in fallback if char.isascii() and char not in {'"', ";"})
    if not ascii_fallback or not any(char.isalnum() for char in ascii_fallback):
        ascii_fallback = "completed-disclosure"
    return {
        "Content-Disposition": (
            f"attachment; filename={ascii_fallback}; "
            f"filename*=UTF-8''{quote(safe_filename)}"
        )
    }


@app.get("/cases/{case_id}/export/completed-disclosure/markdown")
def export_completed_disclosure_markdown(case_id: str):
    markdown, title = _completed_markdown(case_id)
    store.update_case(case_id, {"status": CaseStatus.exported})
    filename = f"{title}-completed-disclosure.md"
    return Response(
        markdown,
        media_type="text/markdown; charset=utf-8",
        headers=_safe_download_headers(filename, "completed-disclosure.md"),
    )


@app.get("/cases/{case_id}/export/completed-disclosure/docx")
def export_completed_disclosure_docx(case_id: str):
    markdown, title = _completed_markdown(case_id)
    content = markdown_to_docx_bytes(markdown, title)
    store.update_case(case_id, {"status": CaseStatus.exported})
    filename = f"{title}-completed-disclosure.docx"
    return Response(
        content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=_safe_download_headers(filename, "completed-disclosure.docx"),
    )


static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
