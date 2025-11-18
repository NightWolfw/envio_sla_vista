from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class EvolutionGroup(BaseModel):
    group_id: str
    nome: str
    cr: Optional[str] = None


class EvolutionGroupsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    grupos: List[EvolutionGroup]


class EvolutionImportRequest(BaseModel):
    grupos: List[EvolutionGroup] = Field(..., min_items=1)


class EvolutionImportResponse(BaseModel):
    inseridos: int
    estrutura_atualizada: int
    erros: List[str]
