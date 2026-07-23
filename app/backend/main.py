"""FastAPI application entry point."""

from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.backend.api.routes_downloads import router as downloads_router
from app.backend.api.routes_health import router as health_router
from app.backend.api.routes_settings import router as settings_router
from app.backend.models.settings import AppSettings
from app.backend.services.download_manager import DownloadManager
from app.backend.utils.logging import configure_logging

FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"


def create_app(
    settings: AppSettings | None = None,
    manager: DownloadManager | None = None,
) -> FastAPI:
    configure_logging()
    api = FastAPI(
        title="LynkOo",
        description="Local media manager with spotDL-backed audio and modular providers.",
        version="0.1.0",
    )
    api.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8800",
            "http://127.0.0.1:8800",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    api.state.download_manager = manager or DownloadManager(settings or AppSettings())
    api.include_router(health_router)
    api.include_router(settings_router)
    api.include_router(downloads_router)

    if FRONTEND_DIST_DIR.is_dir():
        # Serves the built React app (npm run build) so the desktop launcher
        # can point a single window at this server instead of running a
        # separate Vite dev server. Mounted last so it never shadows /api/*.
        api.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")

    return api


app = create_app()


def run() -> None:
    uvicorn.run("app.backend.main:app", host="127.0.0.1", port=8800, reload=False)
