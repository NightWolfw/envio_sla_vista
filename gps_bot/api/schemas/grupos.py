from __future__ import annotations

from typing import Optional

from typing import List

from pydantic import BaseModel, Field


class Grupo(BaseModel):
    id: int
    group_id: str
    nome_grupo: str
    envio: bool
    envio_pdf: bool
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
    envio_pdf: bool
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


class GrupoDeleteRequest(BaseModel):
    ids: List[int] = Field(..., min_items=1)


class GrupoDeleteResponse(BaseModel):
    removidos: int


class GrupoCRItem(BaseModel):
    id: int
    nome_grupo: str
    cr: str
