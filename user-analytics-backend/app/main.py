import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

backend_root = Path(__file__).resolve().parents[1]
load_dotenv(backend_root / ".env")

from app.core.database import SessionLocal
import app.models  # ensure models are registered on Base.metadata
from app.routers import users
from app.routers import analyticsOverview
from app.routers import auth
from app.routers import platform_user
from app.routers import service
from app.routers import userActivity
from app.routers import trialAnalytics
from app.routers import retention
from app.routers import admin_import
from app.routers import campaign_impact
from app.routers import churn_analysis
from app.routers import management
from app.routers import campaign_upload
from app.routers import ml_churn
from app.routers import cross_service
from app.routers import segmentation
from ml_models import anomalies
from app.routers import nrr
from app.routers import notes
from app.routers import reports as reports_router
from app.routers import notifications

from app.core.security import hash_password
from app.models.platform_users import PlatformUser
from app.models.refresh_tokens import RefreshToken
from sqlalchemy.exc import ProgrammingError

app = FastAPI(
    title="User Analytics Platform",
    version="1.0.0",
)

logger = logging.getLogger(__name__)
_refresh_cleanup_task: asyncio.Task | None = None

static_root = os.path.join(os.path.dirname(__file__), "..", "uploads")
avatars_dir = os.path.join(static_root, "avatars")
os.makedirs(avatars_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_root), name="static")

# ⚠️ CORS DOIT être ajouté AVANT tous les routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def latency_logger(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000

    level = logging.WARNING if ms > 3000 else logging.INFO
    logger.log(
        level,
        f"{request.method} {request.url.path} -> {response.status_code} [{ms:.0f}ms]",
    )
    return response

@app.on_event("startup")
async def on_startup():
    global _refresh_cleanup_task
    logger.info("Application started. Use 'alembic upgrade head' for migrations.")
    if _refresh_cleanup_task is None or _refresh_cleanup_task.done():
        _refresh_cleanup_task = asyncio.create_task(_refresh_token_cleanup_loop())

    # Optional: create an initial admin user for dev/demo environments.
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_full_name = os.getenv("ADMIN_FULL_NAME", "Administrator")
    admin_role = os.getenv("ADMIN_ROLE", "admin")

    if admin_email and admin_password:
        db = SessionLocal()
        try:
            existing = (
                db.query(PlatformUser)
                .filter(PlatformUser.email == admin_email)
                .first()
            )
            if not existing:
                user = PlatformUser(
                    email=admin_email,
                    password_hash=hash_password(admin_password),
                    full_name=admin_full_name,
                    role=admin_role,
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(user)
                db.commit()
        finally:
            db.close()


@app.on_event("shutdown")
async def on_shutdown():
    global _refresh_cleanup_task
    if _refresh_cleanup_task and not _refresh_cleanup_task.done():
        _refresh_cleanup_task.cancel()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(analyticsOverview.router)
app.include_router(platform_user.router, prefix="/platform-users", tags=["Platform Users"])
app.include_router(service.router)
app.include_router(userActivity.router)
app.include_router(trialAnalytics.router)
app.include_router(retention.router)
app.include_router(admin_import.router)
app.include_router(campaign_impact.router)
app.include_router(churn_analysis.router)
app.include_router(management.router)
app.include_router(campaign_upload.router)
app.include_router(ml_churn.router)
app.include_router(cross_service.router)
app.include_router(segmentation.router)
app.include_router(anomalies.router)
app.include_router(nrr.router, prefix="/analytics", tags=["NRR"])
app.include_router(notes.router)
app.include_router(reports_router.router)
app.include_router(notifications.router)
@app.get("/")
def root():
    return {"message": "API running"}
async def _refresh_token_cleanup_loop() -> None:
    while True:
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            stale_revoked_before = now.timestamp() - 24 * 60 * 60
            stale_revoked_dt = datetime.fromtimestamp(stale_revoked_before, timezone.utc)
            (
                db.query(RefreshToken)
                .filter(
                    (RefreshToken.expires_at < now)
                    | ((RefreshToken.revoked.is_(True)) & (RefreshToken.created_at < stale_revoked_dt))
                )
                .delete(synchronize_session=False)
            )
            db.commit()
        except ProgrammingError as exc:
            db.rollback()
            # Before migrations are applied, refresh_tokens may not exist yet.
            if "refresh_tokens" in str(exc).lower() and "does not exist" in str(exc).lower():
                logger.info("Skipping refresh-token cleanup: table refresh_tokens not found yet.")
            else:
                logger.exception("Refresh-token cleanup failed.")
        except Exception:
            db.rollback()
            logger.exception("Refresh-token cleanup failed.")
        finally:
            db.close()
        await asyncio.sleep(60 * 60)
