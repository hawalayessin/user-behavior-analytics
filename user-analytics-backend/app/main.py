from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routers import users
from app.routers import analyticsOverview
from app.routers import auth
from app.routers import platform_user
from app.routers import service
from app.routers import userActivity 

app = FastAPI(
    title="User Analytics Platform",
    version="1.0.0",
)

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

@app.on_event("startup")
def on_startup():
    pass

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(analyticsOverview.router)
app.include_router(platform_user.router, prefix="/platform-users", tags=["Platform Users"])
app.include_router(service.router)
app.include_router(userActivity.router) 
@app.get("/")
def root():
    return {"message": "API running"}