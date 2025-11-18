from __future__ import annotations

from datetime import datetime, time
from typing import Literal, Optional

from pydantic import BaseModel, Field, validator


class Agendamento(BaseModel):
    id: int
    grupo_id: int
    nome_grupo: str
    cr: Optional[str]
    tipo_envio: str
    dias_semana: Optional[str]
    data_envio: datetime
    proximo_envio: Optional[str]
    hora_inicio: time
    dia_offset_inicio: int
    hora_fim: time
    dia_offset_fim: int
    ativo: bool
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    ultimo_status: Optional[str] = None
    ultimo_envio: Optional[str] = None
    ultimo_erro: Optional[str] = None


class AgendamentoCreate(BaseModel):
    grupo_id: int
    tipo_envio: Literal["resultados", "programadas"]
    dias_semana: list[str] = Field(default_factory=list)
    data_envio: datetime
    hora_inicio: time
    dia_offset_inicio: int = 0
    hora_fim: time
    dia_offset_fim: int = 0

    @validator("dias_semana")
    def uppercase_days(cls, value: list[str]) -> list[str]:
        return [v.strip().lower() for v in value if v.strip()]


class AgendamentoUpdate(AgendamentoCreate):
    ativo: Optional[bool] = None


class AgendamentoCreatedResponse(BaseModel):
    id: int


class AgendamentoDetail(BaseModel):
    id: int
    grupo_id: int
    tipo_envio: str
    dias_semana: Optional[str]
    data_envio: datetime
    hora_inicio: time
    dia_offset_inicio: int
    hora_fim: time
    dia_offset_fim: int
    ativo: bool
    proximo_envio: Optional[datetime]
    criado_em: datetime
    atualizado_em: Optional[datetime]


class AgendamentoLog(BaseModel):
    id: int
    data_envio: str
    status: str
    mensagem_enviada: Optional[str]
    resposta_api: Optional[str]
    erro: Optional[str]
    criado_em: str
    nome_grupo: Optional[str]


class ToggleResponse(BaseModel):
    id: int
    ativo: bool


class AgendamentoListResponse(BaseModel):
    items: list[Agendamento]
    total: int
    page: int
    page_size: int


class AgendamentoLogList(BaseModel):
    items: list[AgendamentoLog]
    total: int
    page: int
    page_size: int
