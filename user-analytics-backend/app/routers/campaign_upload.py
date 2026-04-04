from __future__ import annotations

import csv
import io
import os
import re
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.dependencies import require_admin


router = APIRouter(prefix="/admin/management/campaigns", tags=["Campaign Upload"])

MAX_FILE_SIZE = 5 * 1024 * 1024
PHONE_REGEX = re.compile(r"^\+?[0-9]{8,15}$")


def _clean_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().strip("'\"")


def _parse_csv(content: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        return []

    rows: list[dict[str, str]] = []
    for row in reader:
        rows.append({k.strip(): _clean_cell(v) for k, v in row.items() if k is not None})
    return rows


def _parse_sql(content: str) -> list[dict[str, str]]:
    insert_match = re.search(
        r"INSERT\s+INTO\s+campaign_targets\s*\(([^)]+)\)\s*VALUES\s*([\s\S]+?);",
        content,
        flags=re.IGNORECASE,
    )
    if not insert_match:
        return []

    columns = [_clean_cell(c).lower() for c in insert_match.group(1).split(",")]
    values_block = insert_match.group(2)
    raw_rows = re.findall(r"\(([^()]*)\)", values_block)

    rows: list[dict[str, str]] = []
    for raw in raw_rows:
        parsed = next(csv.reader([raw], skipinitialspace=True, quotechar="'"))
        values = [_clean_cell(v) for v in parsed]
        mapped = dict(zip(columns, values))
        rows.append(
            {
                "phone_number": mapped.get("phone_number", ""),
                "segment": mapped.get("segment", ""),
                "region": mapped.get("region", ""),
            }
        )
    return rows


@router.post("/upload-targets")
async def upload_targets(
    targets_file: UploadFile = File(...),
    _: object = Depends(require_admin),
):
    filename = targets_file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in {".csv", ".sql"}:
        raise HTTPException(status_code=400, detail="Only .csv and .sql files accepted")

    raw = await targets_file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="File contains no data rows")
    if len(raw) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 5MB limit")

    try:
        text_content = raw.decode("utf-8")
    except UnicodeDecodeError:
        text_content = raw.decode("latin-1")

    if ext == ".csv":
        rows = _parse_csv(text_content)
    else:
        rows = _parse_sql(text_content)

    if not rows:
        raise HTTPException(status_code=400, detail="File contains no data rows")

    sample = rows[0]
    if "phone_number" not in sample:
        raise HTTPException(status_code=400, detail="phone_number column is required")

    seen: set[str] = set()
    valid: list[dict[str, str | None]] = []
    invalid: list[str] = []
    dupes = 0

    for row in rows:
        phone = _clean_cell(row.get("phone_number", ""))
        segment = _clean_cell(row.get("segment", ""))
        region = _clean_cell(row.get("region", ""))

        if not PHONE_REGEX.match(phone):
            if phone:
                invalid.append(phone)
            else:
                invalid.append("<empty>")
            continue

        if phone in seen:
            dupes += 1
            continue

        seen.add(phone)
        valid.append(
            {
                "phone_number": phone,
                "segment": segment or None,
                "region": region or None,
            }
        )

    if not valid:
        raise HTTPException(status_code=400, detail="File contains no data rows")

    return {
        "status": "success",
        "total_parsed": len(rows),
        "valid": len(valid),
        "invalid_count": len(invalid),
        "duplicates_removed": dupes,
        "invalid_phones": invalid[:10],
        "preview": valid[:5],
        "targets": valid,
    }
