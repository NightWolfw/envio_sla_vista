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
    chave = _key(filtros)
    try:
        raw = _client().get(chave)
        if not raw:
            logger.info("[Dashboard] Cache MISS no Redis para chave: %s", chave)
            return None
        data = json.loads(raw)
        last = data.get("last_updated")
        logger.info(
            "[Dashboard] Cache HIT no Redis para chave: %s (last_updated=%s)",
            chave,
            last,
        )
        return data
    except Exception as exc:
        logger.error("Erro ao ler cache do dashboard no Redis (chave=%s): %s", chave, exc)
        return None


def set_cached_dashboard(payload: Dict[str, Any], filtros: Dict[str, Any]) -> None:
    chave = _key(filtros)
    data = dict(payload)
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        _client().set(chave, json.dumps(data))
        logger.info(
            "[Dashboard] Cache SET no Redis (chave=%s, dias=%s, heatmap_cr=%s, total=%s)",
            chave,
            len(data.get("serie_diaria", [])),
            len(data.get("heatmap", [])),
            data.get("pizza", {}).get("total"),
        )
    except Exception as exc:
        logger.error("Erro ao salvar cache do dashboard no Redis (chave=%s): %s", chave, exc)
        raise


def clear_cached_dashboard(filtros: Dict[str, Any] | None = None) -> None:
    try:
        if filtros is None:
            # Limpa todos os dashboards
            keys = _client().keys("dashboard:sla:*")
            if keys:
                _client().delete(*keys)
                logger.info("[Dashboard] Cache CLEAR completo no Redis. Chaves removidas: %s", len(keys))
            else:
                logger.info("[Dashboard] Cache CLEAR solicitado, mas nenhuma chave encontrada.")
        else:
            chave = _key(filtros)
            _client().delete(chave)
            logger.info("[Dashboard] Cache CLEAR no Redis para chave: %s", chave)
    except Exception as exc:
        logger.error("Erro ao limpar cache do dashboard no Redis: %s", exc)
