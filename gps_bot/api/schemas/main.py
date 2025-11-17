from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_grupos: int
    total_mensagens: int
    total_envios: int
    generated_at: datetime
