from __future__ import annotations

from datetime import datetime, time
from typing import Literal, Optional

from pydantic import BaseModel


class SLAPreviewRequest(BaseModel):
    tipo_envio: Literal["resultados", "programadas"] = "resultados"
    data_envio: datetime
    hora_inicio: time
    dia_offset_inicio: int = 0
    hora_fim: time
    dia_offset_fim: int = 0


class SLAPreview(BaseModel):
    grupo_id: int
    grupo_nome: str
    cr: str
    periodo_inicio: datetime
    periodo_fim: datetime
    envio_agendado: datetime
    tipo_envio: str
    stats: dict[str, int]
    mensagem: Optional[str] = None
