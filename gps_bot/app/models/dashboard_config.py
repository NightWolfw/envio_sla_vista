from __future__ import annotations

from datetime import time
from typing import Any, Dict

from app.models.database import get_db_site


def obter_config_dashboard() -> Dict[str, Any]:
    """
    Retorna configuração global do dashboard (único registro).
    """
    conn = get_db_site()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, hora_inicio, hora_fim, intervalo_minutos, monitor_ativo, atualizado_em
        FROM dashboard_config
        ORDER BY id
        LIMIT 1
        """
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return {
            "id": None,
            "hora_inicio": time(0, 0),
            "hora_fim": time(23, 59),
            "intervalo_minutos": 10,
            "monitor_ativo": False,
            "atualizado_em": None,
        }

    return {
        "id": row[0],
        "hora_inicio": row[1],
        "hora_fim": row[2],
        "intervalo_minutos": row[3],
        "monitor_ativo": row[4],
        "atualizado_em": row[5],
    }


def salvar_config_dashboard(intervalo_minutos: int, monitor_ativo: bool) -> Dict[str, Any]:
    """
    Atualiza (ou insere) a configuração global.
    """
    conn = get_db_site()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO dashboard_config (id, hora_inicio, hora_fim, intervalo_minutos, atualizado_em)
        VALUES (1, '00:00', '23:59', %s, NOW())
        ON CONFLICT (id)
        DO UPDATE SET intervalo_minutos = EXCLUDED.intervalo_minutos,
                      monitor_ativo = %s,
                      atualizado_em = NOW()
        RETURNING id, hora_inicio, hora_fim, intervalo_minutos, monitor_ativo, atualizado_em
        """,
        (intervalo_minutos, monitor_ativo),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return {
        "id": row[0],
        "hora_inicio": row[1],
        "hora_fim": row[2],
        "intervalo_minutos": row[3],
        "monitor_ativo": row[4],
        "atualizado_em": row[5],
    }
