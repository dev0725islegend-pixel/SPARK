"""FastAPI application entrypoint"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from backend.app.api.v1 import auth, chat, health
from backend.app.core.config import settings
from backend.app.db.session import engine, Base
import logging

# Create DB tables if they don't exist (for first-run simplicity)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SPARK AI Platform - Backend", version="1.0.0")

# Middleware
origins = [o.strip() for o in settings.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"]) 
app.include_router(chat.router, prefix="/api/v1/conversations", tags=["conversations"]) 
app.include_router(health.router, prefix="/api/v1/health", tags=["health"]) 

# Root
@app.get("/", tags=["root"])
def read_root():
    return {"status": "ok", "service": "spark-backend"}

# Startup logging
@app.on_event("startup")
def startup_event():
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
