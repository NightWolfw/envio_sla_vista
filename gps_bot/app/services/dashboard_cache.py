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
CACHE_KEY = "dashboard:sla:global"


def _client() -> redis.Redis:
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


def get_cached_dashboard() -> Optional[Dict[str, Any]]:
    try:
        raw = _client().get(CACHE_KEY)
        if not raw:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.error(f"Erro ao ler cache do dashboard: {exc}")
        return None


def set_cached_dashboard(payload: Dict[str, Any]) -> None:
    data = dict(payload)
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        _client().set(CACHE_KEY, json.dumps(data))
    except Exception as exc:
        logger.error(f"Erro ao salvar cache do dashboard: {exc}")
        raise


def clear_cached_dashboard() -> None:
    try:
        _client().delete(CACHE_KEY)
    except Exception as exc:
        logger.error(f"Erro ao limpar cache do dashboard: {exc}")
