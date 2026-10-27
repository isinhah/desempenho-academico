from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.escola_dto import EscolaResponse
from app.services.escola_service import EscolaService

router = APIRouter(prefix="/escolas", tags=["Escolas"])


@router.get("", response_model=list[EscolaResponse])
def listar_escolas(db: Session = Depends(get_db)):
    return EscolaService(db).listar_escolas()
