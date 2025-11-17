from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Grupo(BaseModel):
    id: int
    group_id: str
    nome_grupo: str
    envio: bool
    cr: Optional[str] = None
    cliente: Optional[str] = None
    pec_01: Optional[str] = None
    pec_02: Optional[str] = None
    diretor_executivo: Optional[str] = None
    diretor_regional: Optional[str] = None
    gerente_regional: Optional[str] = None
    gerente: Optional[str] = None
    supervisor: Optional[str] = None


class GrupoUpdate(BaseModel):
    group_id: str
    nome: str
    enviar_mensagem: bool
    cr: Optional[str] = None


class GrupoFiltersResponse(BaseModel):
    diretor_executivo: list[str]
    diretor_regional: list[str]
    gerente_regional: list[str]
    gerente: list[str]
    supervisor: list[str]
    cliente: list[str]
    pec_01: list[str]
    pec_02: list[str]
