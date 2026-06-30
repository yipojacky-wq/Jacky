from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class CaseStatus(str, Enum):
    draft = "Draft"
    uploaded = "Uploaded"
    engineering_defined = "Engineering Defined"
    disclosure_completed = "Disclosure Completed"
    engineer_edited = "Engineer Edited"
    ready_for_specification_drafting = "Ready for Specification Drafting"
    exported = "Exported"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SourceDocument(BaseModel):
    filename: str
    content_type: str = "text/plain"
    text: str = ""
    uploaded_at: str = Field(default_factory=utc_now_iso)


class DraftVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = ""
    content: str = ""
    saved_at: str = Field(default_factory=utc_now_iso)


class PatentCase(BaseModel):
    case_id: str = Field(default_factory=lambda: str(uuid4()))
    case_title: str
    client_name: str = ""
    inventors: List[str] = Field(default_factory=list)
    technical_field: str = ""
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)
    status: CaseStatus = CaseStatus.draft
    source_documents: List[SourceDocument] = Field(default_factory=list)
    transcript_or_disclosure_text: str = ""

    # Disclosure Completion AI MVP primary outputs.
    engineering_definition: Dict[str, Any] = Field(default_factory=dict)
    disclosure_completion: Dict[str, Any] = Field(default_factory=dict)
    progressive_elaboration_disclosure: Dict[str, Any] = Field(default_factory=dict)
    embodiment_expansion: Dict[str, Any] = Field(default_factory=dict)
    completed_disclosure_draft: str = ""
    draft_versions: List[DraftVersion] = Field(default_factory=list)

    original_solution: str = ""
    engineering_boundary: str = ""
    project_scope: str = ""

    engineer_notes: str = ""
    engineering_definition_confirmed: bool = False
    completed_disclosure_confirmed: bool = False

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, status):
        if isinstance(status, str) and status.startswith("CaseStatus."):
            status = status.split(".", 1)[1]
        aliases = {
            "draft": CaseStatus.draft,
            "uploaded": CaseStatus.uploaded,
            "engineering_defined": CaseStatus.engineering_defined,
            "disclosure_completed": CaseStatus.disclosure_completed,
            "engineer_edited": CaseStatus.engineer_edited,
            "ready_for_specification_drafting": CaseStatus.ready_for_specification_drafting,
            "exported": CaseStatus.exported,
        }
        return aliases.get(status, status)


class CaseCreate(BaseModel):
    case_title: str
    client_name: str = ""
    inventors: List[str] = Field(default_factory=list)
    technical_field: str = ""
    transcript_or_disclosure_text: str = ""


class CaseUpdate(BaseModel):
    case_title: Optional[str] = None
    client_name: Optional[str] = None
    inventors: Optional[List[str]] = None
    technical_field: Optional[str] = None
    status: Optional[CaseStatus] = None
    source_documents: Optional[List[SourceDocument]] = None
    transcript_or_disclosure_text: Optional[str] = None

    engineering_definition: Optional[Dict[str, Any]] = None
    disclosure_completion: Optional[Dict[str, Any]] = None
    progressive_elaboration_disclosure: Optional[Dict[str, Any]] = None
    embodiment_expansion: Optional[Dict[str, Any]] = None
    completed_disclosure_draft: Optional[str] = None
    draft_versions: Optional[List[DraftVersion]] = None

    original_solution: Optional[str] = None
    engineering_boundary: Optional[str] = None
    project_scope: Optional[str] = None

    engineer_notes: Optional[str] = None
    engineering_definition_confirmed: Optional[bool] = None
    completed_disclosure_confirmed: Optional[bool] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, status):
        return PatentCase.normalize_status(status)
