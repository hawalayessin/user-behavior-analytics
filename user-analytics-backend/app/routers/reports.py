"""Report Generator router."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.report_history import ReportHistory
from app.services.pdf_report_service import PDFReportService
from app.services.report_data_service import (
    fetch_anomalies,
    fetch_campaign_data,
    fetch_churn_data,
    fetch_kpis,
    fetch_segments,
)

router = APIRouter(prefix="/reports", tags=["reports"])

# In-memory active runs store (report_id -> runtime status)
_active_runs: dict[str, dict[str, Any]] = {}

GENERATION_STEPS = [
    "Extraction des KPIs depuis analytics_db",
    "Analyse du churn et de la rétention",
    "Génération des insights IA (Gemini)",
    "Construction des visualisations PDF",
    "Compilation du document final",
]


class ReportRequest(BaseModel):
    report_type: str = "full"
    period_start: str = "2025-09-01"
    period_end: str = "2025-10-31"
    services_included: list[str] = ["ElJournal", "Esports.tn", "ttoons", "Tawer"]
    sections_included: list[str] = [
        "summary",
        "activity",
        "churn",
        "retention",
        "trial",
        "campaigns",
        "ai_segmentation",
    ]
    distribution_format: str = "pdf"
    include_ai_insights: bool = True
    include_recommendations: bool = True
    include_cover_page: bool = True
    anonymize_data: bool = False
    language: str = "fr"
    gemini_prompt_template: str = ""


REPORT_TYPE_SECTIONS: dict[str, list[str]] = {
    "executive": ["summary", "activity"],
    "churn": ["churn", "retention", "trial"],
    "ai_segmentation": ["summary", "ai_segmentation", "campaigns"],
    "full": [
        "summary",
        "activity",
        "churn",
        "retention",
        "trial",
        "campaigns",
        "ai_segmentation",
        "raw_data",
    ],
    "complete": [
        "summary",
        "activity",
        "churn",
        "retention",
        "trial",
        "campaigns",
        "ai_segmentation",
        "raw_data",
    ],
    "premium_enterprise": [
        "summary",
        "activity",
        "churn",
        "retention",
        "trial",
        "campaigns",
        "ai_segmentation",
        "raw_data",
    ],
}


@router.post("/generate")
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report_id = str(uuid.uuid4())
    # Respect explicit section selection from UI; only fallback to report_type defaults if empty.
    if request.sections_included:
        normalized_sections = request.sections_included
    else:
        normalized_sections = REPORT_TYPE_SECTIONS.get(request.report_type, ["summary"])
    request.sections_included = normalized_sections

    _active_runs[report_id] = {
        "report_id": report_id,
        "status": "generating",
        "current_step": GENERATION_STEPS[0],
        "current_step_num": 1,
        "total_steps": len(GENERATION_STEPS),
        "progress_pct": 0,
        "error": None,
        "file_path": None,
        "filename": None,
        "file_size_kb": None,
        "ai_used": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }

    record = ReportHistory(
        id=uuid.UUID(report_id),
        report_type=request.report_type,
        period_start=request.period_start,
        period_end=request.period_end,
        services_included=request.services_included,
        sections_included=request.sections_included,
        distribution_format=request.distribution_format,
        include_ai_insights=request.include_ai_insights,
        include_recommendations=request.include_recommendations,
        status="generating",
        created_by=str(getattr(current_user, "id", "unknown")),
        current_step=GENERATION_STEPS[0],
        current_step_num=1,
        total_steps=len(GENERATION_STEPS),
        progress_pct=0,
    )
    db.add(record)
    db.commit()

    req_payload = request.model_dump()
    req_payload["generated_by_name"] = (
        getattr(current_user, "full_name", None)
        or getattr(current_user, "email", None)
        or "Unknown user"
    )
    req_payload["generated_by_email"] = getattr(current_user, "email", None) or ""
    req_payload["platform_name"] = "DigMaco Analytics"

    background_tasks.add_task(_background_generate, report_id=report_id, request=req_payload)

    return {"report_id": report_id, "status": "generating", "message": "Génération démarrée"}


async def _background_generate(report_id: str, request: dict[str, Any]) -> None:
    from app.core.database import SessionLocal

    run = _active_runs[report_id]
    db = SessionLocal()

    def _update(step_num: int, pct: int) -> None:
        run.update(
            {
                "current_step": GENERATION_STEPS[step_num - 1],
                "current_step_num": step_num,
                "progress_pct": pct,
            }
        )
        db.execute(
            text(
                """
                UPDATE report_history SET
                    current_step = :step,
                    current_step_num = :step_num,
                    progress_pct = :pct
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {
                "step": GENERATION_STEPS[step_num - 1],
                "step_num": step_num,
                "pct": pct,
                "id": report_id,
            },
        )
        db.commit()

    try:
        _update(1, 10)
        kpis = fetch_kpis(
            db,
            period_start=request.get("period_start"),
            period_end=request.get("period_end"),
            services=request.get("services_included"),
        )

        _update(2, 30)
        churn_data = fetch_churn_data(
            db,
            period_start=request.get("period_start"),
            period_end=request.get("period_end"),
            services=request.get("services_included"),
        )
        segments = fetch_segments(
            db,
            period_start=request.get("period_start"),
            period_end=request.get("period_end"),
            services=request.get("services_included"),
        )
        campaign_data = fetch_campaign_data(
            db,
            period_start=request.get("period_start"),
            period_end=request.get("period_end"),
            services=request.get("services_included"),
        )
        anomalies = fetch_anomalies(db)

        _update(3, 50)
        # Step 3: Gemini AI insights are generated inside PDFReportService.generate_pdf()
        # The service handles: Gemini call → fallback merge → template rendering → PDF output

        _update(4, 60)
        svc = PDFReportService()
        result = await svc.generate_pdf(
            report_config=request,
            kpis=kpis,
            churn_data=churn_data,
            segments=segments,
            anomalies=anomalies,
            campaign_data=campaign_data,
        )

        _update(5, 100)
        run.update(
            {
                "status": "success",
                "file_path": result["file_path"],
                "filename": result["filename"],
                "file_size_kb": result["file_size_kb"],
                "ai_used": result["ai_used"],
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        db.execute(
            text(
                """
                UPDATE report_history SET
                    status = 'success',
                    file_path = :fp,
                    file_name = :fn,
                    file_size_kb = :fs,
                    progress_pct = 100,
                    ai_insights_used = :ai,
                    generation_time_sec = :sec,
                    completed_at = NOW()
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {
                "fp": result["file_path"],
                "fn": result["filename"],
                "fs": result["file_size_kb"],
                "ai": result["ai_used"],
                "sec": result["generation_sec"],
                "id": report_id,
            },
        )
        db.commit()
    except Exception as exc:
        run.update(
            {
                "status": "failed",
                "error": str(exc),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        try:
            db.execute(
                text(
                    """
                    UPDATE report_history SET
                        status = 'failed',
                        error_msg = :err,
                        completed_at = NOW()
                    WHERE id = CAST(:id AS uuid)
                    """
                ),
                {"err": str(exc), "id": report_id},
            )
            db.commit()
        except Exception:
            pass
    finally:
        db.close()


@router.get("/status/{report_id}")
async def get_status(report_id: str, current_user=Depends(get_current_user)):
    run = _active_runs.get(report_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Aucun rapport trouvé pour l'ID : {report_id}")
    return run


@router.get("/history")
async def get_history(
    limit: int = 10,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text(
            """
            SELECT
                id, report_type, status,
                file_name, file_size_kb,
                progress_pct, ai_insights_used,
                services_included,
                created_at, completed_at
            FROM report_history
            ORDER BY created_at DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    ).fetchall()

    return [
        {
            "id": str(r.id),
            "report_type": r.report_type,
            "status": r.status,
            "file_name": r.file_name,
            "file_size_kb": r.file_size_kb or 0,
            "progress_pct": r.progress_pct or 0,
            "ai_used": r.ai_insights_used or 0,
            "services": r.services_included or [],
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        }
        for r in rows
    ]


@router.get("/download/{report_id}")
async def download_report(
    report_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    run = _active_runs.get(report_id)
    file_path = run.get("file_path") if run else None

    if not file_path:
        row = db.execute(
            text(
                """
                SELECT file_path
                FROM report_history
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {"id": report_id},
        ).fetchone()
        file_path = row.file_path if row else None

    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="Fichier PDF introuvable.")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=Path(file_path).name,
        headers={"Content-Disposition": f'attachment; filename="{Path(file_path).name}"'},
    )
