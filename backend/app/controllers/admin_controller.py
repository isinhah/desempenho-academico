import os
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.domain.importacao_csv import processar_importacao_storage
from app.dtos.importacao_dto import (
    ImportacaoProcessadaResponse,
    ProcessarImportacaoRequest,
)

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


@router.post(
    "/importacoes/processar",
    response_model=ImportacaoProcessadaResponse,
    status_code=status.HTTP_201_CREATED,
)
def processar_importacao(
    dados: ProcessarImportacaoRequest,
    _: None = Depends(validar_token_admin),
) -> ImportacaoProcessadaResponse:
    resultado = processar_importacao_storage(dados.caminho_storage)
    return ImportacaoProcessadaResponse(
        importacao_id=resultado.importacao_id,
        caminho_storage=resultado.caminho_storage,
        mes_referencia=resultado.mes_referencia,
        linhas_lidas=resultado.linhas_lidas,
        linhas_importadas=resultado.linhas_importadas,
        registros_sincronizados=resultado.registros_sincronizados,
        status=resultado.status,
    )
