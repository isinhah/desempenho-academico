from fastapi import APIRouter, Depends

from app.auth import obter_usuario_autenticado
from app.dtos.autenticacao_dto import UsuarioAtualResponse
from app.services.autorizacao_service import UsuarioAutenticado

router = APIRouter(prefix="/autenticacao", tags=["Autenticação"])


@router.get("/me", response_model=UsuarioAtualResponse)
def obter_usuario_atual(
    usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado),
) -> UsuarioAtualResponse:
    return UsuarioAtualResponse(
        id=usuario.id,
        nome=usuario.nome,
        papel=usuario.papel,
        cursos_ids=list(usuario.cursos_ids),
    )
