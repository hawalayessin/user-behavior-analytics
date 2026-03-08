from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routers import users
from app.routers import analyticsOverview
from app.routers import auth

app = FastAPI(
    title="User Analytics Platform",
    version="1.0.0",
)

# ─── CORS Configuration ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    pass


# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(users.router)          # ✅ ajoute cette ligne
app.include_router(analyticsOverview.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "API running"}
