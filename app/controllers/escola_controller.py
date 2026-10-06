"""Rotas HTTP de escolas."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.escola_dto import EscolaCreateRequest, EscolaResponse
from app.services.escola_service import EscolaService

router = APIRouter(prefix="/escolas", tags=["Escolas"])


@router.get("", response_model=list[EscolaResponse])
def listar_escolas(db: Session = Depends(get_db)):
    return EscolaService(db).listar_escolas()


@router.post("", response_model=EscolaResponse, status_code=status.HTTP_201_CREATED)
def criar_escola(dados: EscolaCreateRequest, db: Session = Depends(get_db)):
    return EscolaService(db).criar_escola(dados)
