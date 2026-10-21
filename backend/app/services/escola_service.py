"""Consultas analíticas relacionadas a escolas."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dtos.escola_dto import EscolaResponse
from app.models import Escola


class EscolaService:
    def __init__(self, db: Session):
        self.db = db

    def listar_escolas(self) -> list[EscolaResponse]:
        escolas = self.db.scalars(select(Escola).order_by(Escola.nome)).all()
        return [EscolaResponse.model_validate(escola) for escola in escolas]
