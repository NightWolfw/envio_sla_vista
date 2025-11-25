from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import redis

import config as project_config

logger = logging.getLogger(__name__)

REDIS_URL = getattr(project_config, "REDIS_URL", os.getenv("DASHBOARD_REDIS_URL", "redis://redis:6379/2"))


def _client() -> redis.Redis:
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


def _key(filtros: Dict[str, Any]) -> str:
    # Cria chave determinística a partir dos filtros (diretor fixo etc.)
    items = sorted((k, v) for k, v in filtros.items() if v is not None)
    return "dashboard:sla:" + "|".join(f"{k}={v}" for k, v in items)


def get_cached_dashboard(filtros: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        raw = _client().get(_key(filtros))
        if not raw:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.error(f"Erro ao ler cache do dashboard: {exc}")
        return None


def set_cached_dashboard(payload: Dict[str, Any], filtros: Dict[str, Any]) -> None:
    data = dict(payload)
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        _client().set(_key(filtros), json.dumps(data))
    except Exception as exc:
        logger.error(f"Erro ao salvar cache do dashboard: {exc}")
        raise


def clear_cached_dashboard(filtros: Dict[str, Any] | None = None) -> None:
    try:
        if filtros is None:
            # Limpa todos os dashboards
            keys = _client().keys("dashboard:sla:*")
            if keys:
                _client().delete(*keys)
        else:
            _client().delete(_key(filtros))
    except Exception as exc:
        logger.error(f"Erro ao limpar cache do dashboard: {exc}")
