"""Contratos HTTP relacionados a escolas."""

from pydantic import BaseModel, ConfigDict


class EscolaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
