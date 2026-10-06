"""Contratos HTTP relacionados a cursos."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CursoCreateRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=255)
    escola_id: int = Field(gt=0)
    alunos_ativos: int = Field(ge=0, description="Quantidade de alunos ativos")
    alunos_evadidos: int = Field(ge=0, description="Quantidade de alunos evadidos")

    @model_validator(mode="after")
    def validar_quantidades(self) -> "CursoCreateRequest":
        if self.alunos_evadidos > self.alunos_ativos:
            raise ValueError("alunos_evadidos não pode ser maior que alunos_ativos")
        return self


class CursoUpdateRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    alunos_ativos: int | None = Field(default=None, ge=0)
    alunos_evadidos: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validar_quantidades_informadas(self) -> "CursoUpdateRequest":
        if (
            self.alunos_ativos is not None
            and self.alunos_evadidos is not None
            and self.alunos_evadidos > self.alunos_ativos
        ):
            raise ValueError("alunos_evadidos não pode ser maior que alunos_ativos")
        return self


class CursoResponse(BaseModel):
    """Resumo usado na listagem de cursos com score."""

    id: int
    nome: str
    escola: str
    score: float
    classe: str


class CursoDetalheResponse(CursoResponse):
    alunos_ativos: int
    alunos_evadidos: int
    pct_evasao: float | None = None
    mes_referencia: date | None = None


class CursoListResponse(BaseModel):
    """Representação direta de curso e último indicador persistido."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    escola: str
    alunos_ativos: int
    alunos_evadidos: int
    pct_evasao: float | None = None
    mes_referencia: date | None = None
