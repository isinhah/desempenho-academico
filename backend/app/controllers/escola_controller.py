from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import obter_usuario_autenticado
from app.dtos.escola_dto import EscolaResponse
from app.services.escola_service import EscolaService
from app.services.autorizacao_service import UsuarioAutenticado, exigir_visao_geral

router = APIRouter(prefix="/escolas", tags=["Escolas"])


@router.get("", response_model=list[EscolaResponse])
def listar_escolas(
    db: Session = Depends(get_db),
    usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado),
):
    exigir_visao_geral(usuario)
    return EscolaService(db).listar_escolas()
