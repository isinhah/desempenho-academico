"""Rotas HTTP de cursos."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.curso_dto import (
    CursoDetalheResponse,
    HistoricoIndicadorResponse,
    CursoResponse,
)
from app.services.curso_service import CursoService

router = APIRouter(prefix="/cursos", tags=["Cursos"])

@router.get("", response_model=list[CursoResponse])
def listar_cursos(
    escola_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    return CursoService(db).listar_cursos_com_score(escola_id=escola_id)


@router.get("/{curso_id}", response_model=CursoDetalheResponse)
def obter_curso(curso_id: int, db: Session = Depends(get_db)):
    return CursoService(db).obter_curso(curso_id)


@router.get("/{curso_id}/historico", response_model=list[HistoricoIndicadorResponse])
def listar_historico_curso(curso_id: int, db: Session = Depends(get_db)):
    return CursoService(db).listar_historico(curso_id)
