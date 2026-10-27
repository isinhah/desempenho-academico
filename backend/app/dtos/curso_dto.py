from datetime import date

from pydantic import BaseModel


class CursoResponse(BaseModel):
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


class HistoricoIndicadorResponse(BaseModel):
    mes_referencia: date
    pct_evasao: float
