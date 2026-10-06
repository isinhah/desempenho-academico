"""Regras de negócio e persistência de escolas."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dtos.escola_dto import EscolaCreateRequest, EscolaResponse
from app.models import Escola


class EscolaService:
    def __init__(self, db: Session):
        self.db = db

    def listar_escolas(self) -> list[EscolaResponse]:
        escolas = self.db.scalars(select(Escola).order_by(Escola.nome)).all()
        return [EscolaResponse.model_validate(escola) for escola in escolas]

    def criar_escola(self, dados: EscolaCreateRequest) -> EscolaResponse:
        existe = self.db.scalar(select(Escola.id).where(Escola.nome == dados.nome))
        if existe is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma escola com este nome.",
            )

        escola = Escola(nome=dados.nome)
        self.db.add(escola)
        self.db.commit()
        self.db.refresh(escola)
        return EscolaResponse.model_validate(escola)
