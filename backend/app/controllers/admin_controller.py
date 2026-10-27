import os
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.domain.sincronizar_dados_cursos import executar_etl

router = APIRouter(prefix="/administracao", tags=["Administração"])


def validar_token_admin(
    x_admin_token: str | None = Header(default=None),
) -> None:
    token_configurado = os.getenv("ADMIN_API_TOKEN")

    if not token_configurado or not x_admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autorizado.",
        )

    if not secrets.compare_digest(x_admin_token, token_configurado):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autorizado.",
        )


@router.post("/sincronizar-dados", status_code=status.HTTP_200_OK)
def sincronizar_dados(_: None = Depends(validar_token_admin)) -> dict[str, str | int]:
    registros_sincronizados = executar_etl()
    return {
        "mensagem": "Dados sincronizados com sucesso.",
        "registros_sincronizados": registros_sincronizados,
    }
