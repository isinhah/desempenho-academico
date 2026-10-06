"""Contratos padronizados das respostas de erro da API."""

from typing import Any

from pydantic import BaseModel, Field


class ValidationErrorDetail(BaseModel):
    campo: str
    mensagem: str
    tipo: str


class ErrorResponse(BaseModel):
    status: int
    codigo: str
    mensagem: str
    detalhes: list[ValidationErrorDetail] = Field(default_factory=list)


class ErrorResponseExample:
    """Exemplos reutilizáveis para documentação das rotas, quando necessário."""

    NOT_FOUND: dict[str, Any] = {
        "status": 404,
        "codigo": "recurso_nao_encontrado",
        "mensagem": "Curso não encontrado.",
        "detalhes": [],
    }
