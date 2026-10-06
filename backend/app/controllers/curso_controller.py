"""Rotas HTTP de cursos."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.curso_dto import (
    CursoCreateRequest,
    CursoDetalheResponse,
    HistoricoIndicadorResponse,
    CursoResponse,
    CursoUpdateRequest,
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


@router.post("", response_model=CursoDetalheResponse, status_code=status.HTTP_201_CREATED)
def criar_curso(dados: CursoCreateRequest, db: Session = Depends(get_db)):
    return CursoService(db).criar_curso(dados)


@router.patch("/{curso_id}", response_model=CursoDetalheResponse)
def atualizar_curso(
    curso_id: int, dados: CursoUpdateRequest, db: Session = Depends(get_db)
):
    return CursoService(db).atualizar_curso(curso_id, dados)


@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_curso(curso_id: int, db: Session = Depends(get_db)) -> Response:
    CursoService(db).excluir_curso(curso_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
