import json
import os
from pathlib import Path
from typing import List

from .models import CaseCreate, CaseStatus, CaseUpdate, PatentCase, utc_now_iso


class JsonCaseStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _read(self) -> List[PatentCase]:
        raw = json.loads(self.path.read_text(encoding="utf-8") or "[]")
        return [PatentCase.model_validate(item) for item in raw]

    def _write(self, cases: List[PatentCase]) -> None:
        payload = [case.model_dump(mode="json") for case in cases]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def list_cases(self) -> List[PatentCase]:
        return sorted(self._read(), key=lambda item: item.updated_at, reverse=True)

    def get_case(self, case_id: str) -> PatentCase:
        for case in self._read():
            if case.case_id == case_id:
                return case
        raise KeyError(case_id)

    def create_case(self, payload: CaseCreate) -> PatentCase:
        case = PatentCase(**payload.model_dump())
        if case.transcript_or_disclosure_text:
            case.status = CaseStatus.uploaded
        cases = self._read()
        cases.append(case)
        self._write(cases)
        return case

    def update_case(self, case_id: str, payload: CaseUpdate | dict) -> PatentCase:
        updates = payload if isinstance(payload, dict) else payload.model_dump(exclude_unset=True)
        cases = self._read()
        for index, case in enumerate(cases):
            if case.case_id == case_id:
                data = case.model_dump()
                data.update(updates)
                data["updated_at"] = utc_now_iso()
                updated = PatentCase.model_validate(data)
                cases[index] = updated
                self._write(cases)
                return updated
        raise KeyError(case_id)

    def delete_case(self, case_id: str) -> None:
        cases = self._read()
        remaining = [case for case in cases if case.case_id != case_id]
        if len(remaining) == len(cases):
            raise KeyError(case_id)
        self._write(remaining)

    def delete_all_cases(self) -> None:
        self._write([])


def make_store() -> JsonCaseStore:
    return JsonCaseStore(os.getenv("APP_STORAGE_PATH", "app/data/cases.json"))
