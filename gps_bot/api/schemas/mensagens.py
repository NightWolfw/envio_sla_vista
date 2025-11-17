from __future__ import annotations

from datetime import date, time, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, validator


class MensagemBase(BaseModel):
    mensagem: str
    grupos_ids: list[str] = Field(..., min_items=1)
    tipo_recorrencia: Literal["UNICA", "RECORRENTE"] = "UNICA"
    dias_semana: Optional[list[int]] = None
    horario: time
    data_inicio: date
    data_fim: Optional[date] = None

    @validator("grupos_ids")
    def normalizar_grupos(cls, value: list[str]) -> list[str]:
        return [v for v in value if v]


class MensagemCreate(MensagemBase):
    pass


class MensagemUpdate(MensagemBase):
    ativo: Optional[bool] = None


class Mensagem(MensagemBase):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: Optional[datetime] = None


class MensagemToggleResponse(BaseModel):
    id: int
    ativo: bool
