from __future__ import annotations

from typing import Dict

from app.models.database import get_db_site

DEFAULT_RESULTADOS_TEMPLATE = """{{saudacao}} pessoal, tudo bem?

Tarefas Realizadas no período de {{periodo_inicio}} até {{periodo_fim}}

✅ Tarefas finalizadas: {{finalizadas}}
❌ Tarefas não realizadas: {{nao_realizadas}}
📝 Tarefas em aberto: {{em_aberto}}
🔄 Tarefas iniciadas mas não finalizadas: {{iniciadas}}

{{emoji}} Porcentagem de tarefas realizadas/programadas: *{{porcentagem}}%*

{{feedback}}

O detalhamento das tarefas será enviado abaixo para análise, grato pela colaboração de todos!"""

DEFAULT_PROGRAMADAS_TEMPLATE = """{{saudacao}} pessoal, tudo bem?

Tarefas Programadas para o período de {{periodo_completo}}

📝 Tarefas em aberto: {{em_aberto}}
🔄 Tarefas iniciadas mas não finalizadas: {{iniciadas}}

📊 Total de tarefas programadas: *{{total_programadas}}*

O detalhamento das tarefas será enviado abaixo para análise, grato pela colaboração de todos!"""


def _ensure_table() -> None:
    conn = get_db_site()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sla_templates (
            id SERIAL PRIMARY KEY,
            template_key VARCHAR(30) UNIQUE NOT NULL,
            content TEXT NOT NULL,
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()


def get_sla_templates() -> Dict[str, str]:
    _ensure_table()
    conn = get_db_site()
    cur = conn.cursor()
    cur.execute("SELECT template_key, content FROM sla_templates")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    templates = {row[0]: row[1] for row in rows}
    if "resultados" not in templates:
        templates["resultados"] = DEFAULT_RESULTADOS_TEMPLATE
    if "programadas" not in templates:
        templates["programadas"] = DEFAULT_PROGRAMADAS_TEMPLATE
    return templates


def update_sla_templates(resultados: str, programadas: str) -> Dict[str, str]:
    _ensure_table()
    conn = get_db_site()
    cur = conn.cursor()
    upsert_sql = """
        INSERT INTO sla_templates (template_key, content, updated_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (template_key) DO UPDATE
        SET content = EXCLUDED.content,
            updated_at = NOW()
    """
    cur.execute(upsert_sql, ("resultados", resultados))
    cur.execute(upsert_sql, ("programadas", programadas))
    conn.commit()
    cur.close()
    conn.close()
    return {"resultados": resultados, "programadas": programadas}
