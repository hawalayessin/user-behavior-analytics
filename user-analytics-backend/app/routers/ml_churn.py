from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
import threading
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.cache import build_cache_key, cache_or_compute
from app.core.config import settings
from ml_models.churn_predictor import ChurnPredictor

from app.schemas.ml_churn import (
    ChurnScoresResponse,
    ChurnTrainMetricsResponse,
)


router = APIRouter(prefix="/ml/churn", tags=["AI Churn Prediction"])
_train_jobs: dict[str, dict[str, Any]] = {}


def _ensure_scores_cache_table(db: Session) -> None:
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS churn_scores_cache (
            user_id uuid NOT NULL,
            phone_number text,
            service_name text,
            churn_risk double precision NOT NULL,
            risk_category text NOT NULL,
            predicted_churn integer NOT NULL,
            threshold double precision NOT NULL,
            generated_at timestamptz NOT NULL,
            PRIMARY KEY (user_id)
        )
    """))
    db.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_churn_scores_cache_generated_at
        ON churn_scores_cache (generated_at DESC)
    """))
    db.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_churn_scores_cache_risk
        ON churn_scores_cache (churn_risk DESC)
    """))
    db.commit()


def _store_scores_snapshot(db: Session, df_user, threshold: float) -> None:
    _ensure_scores_cache_table(db)
    generated_at = datetime.now(timezone.utc)
    db.execute(text("TRUNCATE TABLE churn_scores_cache"))
    for row in df_user.itertuples(index=False):
        db.execute(
            text("""
                INSERT INTO churn_scores_cache (
                    user_id,
                    phone_number,
                    service_name,
                    churn_risk,
                    risk_category,
                    predicted_churn,
                    threshold,
                    generated_at
                ) VALUES (
                    CAST(:user_id AS uuid),
                    :phone_number,
                    :service_name,
                    :churn_risk,
                    :risk_category,
                    :predicted_churn,
                    :threshold,
                    :generated_at
                )
                ON CONFLICT (user_id) DO UPDATE SET
                    phone_number = EXCLUDED.phone_number,
                    service_name = EXCLUDED.service_name,
                    churn_risk = EXCLUDED.churn_risk,
                    risk_category = EXCLUDED.risk_category,
                    predicted_churn = EXCLUDED.predicted_churn,
                    threshold = EXCLUDED.threshold,
                    generated_at = EXCLUDED.generated_at
            """),
            {
                "user_id": str(row.user_id),
                "phone_number": row.phone_number,
                "service_name": row.service_name,
                "churn_risk": float(row.churn_risk),
                "risk_category": row.risk_category,
                "predicted_churn": int(row.predicted_churn),
                "threshold": float(threshold),
                "generated_at": generated_at,
            },
        )
    db.commit()


def _read_scores_snapshot(db: Session, top: int, threshold: float) -> Optional[ChurnScoresResponse]:
    _ensure_scores_cache_table(db)
    latest = db.execute(text("SELECT MAX(generated_at) AS generated_at FROM churn_scores_cache")).fetchone()
    if latest is None or latest.generated_at is None:
        return None

    distribution_rows = db.execute(text("""
        SELECT risk_category, COUNT(*) AS cnt
        FROM churn_scores_cache
        GROUP BY risk_category
    """)).fetchall()
    distribution_map = {r.risk_category: int(r.cnt or 0) for r in distribution_rows}

    top_rows = db.execute(
        text("""
            SELECT user_id, phone_number, service_name, churn_risk, risk_category, predicted_churn
            FROM churn_scores_cache
            WHERE churn_risk >= :threshold
            ORDER BY churn_risk DESC
            LIMIT :top
        """),
        {"threshold": float(threshold), "top": int(top)},
    ).fetchall()

    total_scored = db.execute(text("SELECT COUNT(*) AS cnt FROM churn_scores_cache")).scalar() or 0

    return ChurnScoresResponse(
        generated_at=latest.generated_at.isoformat(),
        threshold=threshold,
        distribution=[
            {"risk_category": "Low", "count": int(distribution_map.get("Low", 0))},
            {"risk_category": "Medium", "count": int(distribution_map.get("Medium", 0))},
            {"risk_category": "High", "count": int(distribution_map.get("High", 0))},
        ],
        top_users=[
            {
                "user_id": str(r.user_id),
                "phone_number": r.phone_number,
                "service_name": r.service_name,
                "churn_risk": float(r.churn_risk),
                "risk_category": r.risk_category,
                "predicted_churn": int(r.predicted_churn),
            }
            for r in top_rows
        ],
        active_users_scored=int(total_scored),
    )


@router.post("/train", response_model=ChurnTrainMetricsResponse)
def train_churn_model(
    db: Session = Depends(get_db),
    _: Any = Depends(require_admin),
):
    predictor = ChurnPredictor()
    try:
        metrics = predictor.train(db)
    except Exception as e:
        detail = str(e)
        if "statement timeout" in detail.lower():
            raise HTTPException(
                status_code=504,
                detail="Churn training timed out on feature query. Increase CHURN_SQL_TIMEOUT_MS or optimize source indexes.",
            )
        raise HTTPException(status_code=400, detail=detail)
    # If roc_auc couldn't be computed (single class), keep roc_auc=None
    return metrics


@router.post("/train/start")
def start_churn_training_job(
    _: Any = Depends(require_admin),
):
    active = [j for j in _train_jobs.values() if j.get("status") == "running"]
    if active:
        raise HTTPException(status_code=409, detail="A churn training job is already running.")

    job_id = str(uuid.uuid4())
    _train_jobs[job_id] = {
        "job_id": job_id,
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "logs": [{"ts": datetime.now(timezone.utc).isoformat(), "message": "Training job started"}],
        "metrics": None,
        "error": None,
    }

    t = threading.Thread(target=_run_churn_training_job, args=(job_id,), daemon=True)
    t.start()
    return {"job_id": job_id, "status": "running"}


@router.get("/train/{job_id}/status")
def get_churn_training_job_status(
    job_id: str,
    _: Any = Depends(require_admin),
):
    job = _train_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found.")
    return job


def _run_churn_training_job(job_id: str) -> None:
    from app.core.database import SessionLocal

    job = _train_jobs[job_id]
    db = SessionLocal()

    def log_step(message: str, **extra: Any) -> None:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "message": message,
            **extra,
        }
        job["logs"].append(payload)
        if len(job["logs"]) > 200:
            job["logs"] = job["logs"][-200:]

    try:
        predictor = ChurnPredictor()
        metrics = predictor.train(db, progress_callback=log_step)
        job["metrics"] = metrics
        job["status"] = "success"
        job["completed_at"] = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        detail = str(e)
        log_step("Training failed", error=detail)
        job["status"] = "failed"
        job["error"] = detail
        job["completed_at"] = datetime.now(timezone.utc).isoformat()
    finally:
        db.close()


@router.get("/metrics")
def get_churn_model_metrics():
    predictor = ChurnPredictor()
    metrics = predictor.load_metrics()
    if metrics is None:
        raise HTTPException(status_code=404, detail="Churn model not trained yet.")
    return metrics


@router.get("/governance")
def get_churn_model_governance(
    db: Session = Depends(get_db),
):
    cache_key = build_cache_key("ml:churn:governance", {"v": "governance-v2"})

    def _compute() -> dict[str, Any]:
        predictor = ChurnPredictor()
        try:
            return predictor.governance_report(db)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return cache_or_compute(
        cache_key,
        settings.ML_METRICS_CACHE_TTL_SECONDS,
        compute_function=lambda: jsonable_encoder(_compute()),
    )


@router.get("/scores", response_model=ChurnScoresResponse)
def get_churn_scores(
    db: Session = Depends(get_db),
    top: int = Query(default=10, ge=1, le=200),
    threshold: float | None = Query(default=None, ge=0.0, le=1.0),
    store: bool = Query(default=False, description="Store predictions into SQL table churn_predictions."),
    use_cached: bool = Query(default=True, description="Read precomputed scores from churn_scores_cache when available."),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    service_id: str | None = Query(default=None),
):
    has_filters = bool(start_date or end_date or service_id)

    if store:
        return _compute_churn_scores(
            db,
            top=top,
            threshold=threshold,
            store=store,
            use_cached=False,
            service_id=service_id,
            start_date=start_date,
            end_date=end_date,
        )

    cache_key = build_cache_key(
        "ml:churn:scores",
        {
            "top": int(top),
            "threshold": float(threshold),
            "store": bool(store),
            "use_cached": bool(use_cached),
            "service_id": service_id or "all",
            "start_date": start_date or "auto",
            "end_date": end_date or "auto",
        },
    )

    return cache_or_compute(
        cache_key,
        settings.ML_SCORES_CACHE_TTL_SECONDS,
        compute_function=lambda: jsonable_encoder(
            _compute_churn_scores(
                db,
                top=top,
                threshold=threshold,
                store=store,
                use_cached=(use_cached and not has_filters),
                service_id=service_id,
                start_date=start_date,
                end_date=end_date,
            )
        ),
    )


def _compute_churn_scores(
    db: Session,
    *,
    top: int,
    threshold: float | None,
    store: bool,
    use_cached: bool,
    service_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> ChurnScoresResponse:
    if use_cached:
        predictor_for_threshold = ChurnPredictor()
        resolved_threshold = predictor_for_threshold._resolve_threshold(threshold)
        cached_snapshot = _read_scores_snapshot(db, top=top, threshold=resolved_threshold)
        if cached_snapshot is not None:
            return cached_snapshot

    predictor = ChurnPredictor()
    resolved_threshold = predictor._resolve_threshold(threshold)

    try:
        result = predictor.predict_active_subscriptions(
            db,
            threshold=resolved_threshold,
            store_predictions=store,
            service_id=service_id,
            start_date=start_date,
            end_date=end_date,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    df = result.df
    if df.empty:
        now = datetime.now(timezone.utc).isoformat()
        return ChurnScoresResponse(
            generated_at=now,
            threshold=resolved_threshold,
            distribution=[
                {"risk_category": "Low", "count": 0},
                {"risk_category": "Medium", "count": 0},
                {"risk_category": "High", "count": 0},
            ],
            top_users=[],
            active_users_scored=0,
        )

    # Convert to user-level: one row per user, with max churn risk across subscriptions.
    df_sorted = df.sort_values(["user_id", "churn_risk"], ascending=[True, False])
    df_user = df_sorted.groupby("user_id").head(1).copy()
    df_user["user_id"] = df_user["user_id"].astype(str)

    if store:
        _store_scores_snapshot(db, df_user, threshold=resolved_threshold)

    distribution_dict = df_user["risk_category"].value_counts().to_dict()
    distribution = [
        {"risk_category": "Low", "count": int(distribution_dict.get("Low", 0))},
        {"risk_category": "Medium", "count": int(distribution_dict.get("Medium", 0))},
        {"risk_category": "High", "count": int(distribution_dict.get("High", 0))},
    ]

    # "Top risky users" should honor the selected risk threshold.
    top_df = (
        df_user[df_user["churn_risk"] >= resolved_threshold]
        .sort_values("churn_risk", ascending=False)
        .head(top)
    )

    top_users = [
        {
            "user_id": row.user_id,
            "phone_number": row.phone_number,
            "service_name": row.service_name,
            "churn_risk": float(row.churn_risk),
            "risk_category": row.risk_category,
            "predicted_churn": int(row.predicted_churn),
        }
        for _, row in top_df.iterrows()
    ]

    return ChurnScoresResponse(
        generated_at=datetime.now(timezone.utc).isoformat(),
        threshold=resolved_threshold,
        distribution=distribution,
        top_users=top_users,
        active_users_scored=int(df_user["user_id"].nunique()),
    )


@router.post("/scores/recompute", response_model=ChurnScoresResponse)
def recompute_scores_snapshot(
    db: Session = Depends(get_db),
    _: Any = Depends(require_admin),
    threshold: float | None = Query(default=None, ge=0.0, le=1.0),
):
    predictor = ChurnPredictor()
    resolved_threshold = predictor._resolve_threshold(threshold)
    result = predictor.predict_active_subscriptions(
        db,
        threshold=resolved_threshold,
        store_predictions=False,
    )
    df = result.df
    if df.empty:
        _ensure_scores_cache_table(db)
        db.execute(text("TRUNCATE TABLE churn_scores_cache"))
        db.commit()
        return ChurnScoresResponse(
            generated_at=datetime.now(timezone.utc).isoformat(),
            threshold=resolved_threshold,
            distribution=[
                {"risk_category": "Low", "count": 0},
                {"risk_category": "Medium", "count": 0},
                {"risk_category": "High", "count": 0},
            ],
            top_users=[],
            active_users_scored=0,
        )

    df_sorted = df.sort_values(["user_id", "churn_risk"], ascending=[True, False])
    df_user = df_sorted.groupby("user_id").head(1).copy()
    df_user["user_id"] = df_user["user_id"].astype(str)
    _store_scores_snapshot(db, df_user, threshold=resolved_threshold)

    snapshot = _read_scores_snapshot(db, top=10, threshold=resolved_threshold)
    if snapshot is None:
        raise HTTPException(status_code=500, detail="Failed to read churn scores snapshot after recompute")
    return snapshot

