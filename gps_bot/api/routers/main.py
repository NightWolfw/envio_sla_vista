from __future__ import annotations

from datetime import datetime

import pytz

from fastapi import APIRouter, HTTPException

from app.models.database import get_db_site
from api.schemas.main import OverviewStats

router = APIRouter()
TIMEZONE_BRASILIA = pytz.timezone("America/Sao_Paulo")


@router.get("/stats", response_model=OverviewStats)
def obter_estatisticas() -> OverviewStats:
    """Retorna estatísticas gerais do sistema."""
    try:
        conn = get_db_site()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM grupos_whatsapp")
        total_grupos = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM mensagens WHERE ativo = true")
        total_mensagens = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM logs_envio")
        total_envios = cur.fetchone()[0]

        cur.close()
        conn.close()

        return OverviewStats(
            total_grupos=total_grupos,
            total_mensagens=total_mensagens,
            total_envios=total_envios,
            generated_at=datetime.now(TIMEZONE_BRASILIA),
        )
    except Exception as exc:  # pragma: no cover - apenas logging
        raise HTTPException(status_code=500, detail=str(exc)) from exc
