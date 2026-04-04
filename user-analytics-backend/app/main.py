from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import logging
from datetime import datetime, timezone

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

from app.core.security import hash_password
from app.models.platform_users import PlatformUser

app = FastAPI(
    title="User Analytics Platform",
    version="1.0.0",
)

logger = logging.getLogger(__name__)

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
    logger.info("Application started. Use 'alembic upgrade head' for migrations.")

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
@app.get("/")
def root():
    return {"message": "API running"}
