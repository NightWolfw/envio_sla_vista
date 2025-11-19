from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

import config as project_config

router = APIRouter()

PDF_DIR = project_config.PDF_STORAGE_DIR


def _safe_path(filename: str) -> Path:
    candidate = (PDF_DIR / filename).resolve()
    if candidate.parent != PDF_DIR or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return candidate


@router.get("/sla/{filename}", response_class=FileResponse)
def obter_pdf_sla(filename: str):
    if ".." in filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")

    file_path = _safe_path(filename)
    return FileResponse(file_path, media_type="application/pdf", filename=filename)
