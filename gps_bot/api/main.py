from __future__ import annotations

import os
from typing import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import (
    agendamentos,
    dashboard,
    envio,
    grupos,
    mensagens,
    sla,
    main as main_router,
    evolution,
)
from app.services.scheduler_service import iniciar_scheduler, parar_scheduler


def _get_allowed_origins() -> Sequence[str]:
    """
    Returns the list of origins allowed by CORS.
    Uses comma-separated values from API_CORS_ORIGINS env var or allows all.
    """
    raw = os.getenv("API_CORS_ORIGINS")
    if not raw:
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="GPS SLA FastAPI", version="0.1.0", docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router.router, prefix="/api", tags=["Overview"])
app.include_router(grupos.router, prefix="/api/grupos", tags=["Grupos"])
app.include_router(agendamentos.router, prefix="/api/agendamentos", tags=["Agendamentos"])
app.include_router(mensagens.router, prefix="/api/mensagens", tags=["Mensagens"])
app.include_router(envio.router, prefix="/api/envio", tags=["Envio"])
app.include_router(sla.router, prefix="/api/sla", tags=["SLA"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(evolution.router, prefix="/api/evolution", tags=["Evolution API"])


@app.on_event("startup")
def startup_event() -> None:
    """Inicializa recursos globais."""
    iniciar_scheduler()


@app.on_event("shutdown")
def shutdown_event() -> None:
    """Finaliza recursos globais."""
    parar_scheduler()


@app.get("/health", tags=["Health"])
def healthcheck() -> dict[str, str]:
    """Simple health endpoint for monitoring."""
    return {"status": "ok"}
