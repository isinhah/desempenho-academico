from fastapi import APIRouter, Body, Depends, Header, Query, status

from app.auth import obter_usuario_autenticado
from app.domain.importacao_csv import (
    listar_importacoes,
    processar_importacao_storage,
    processar_upload_csv,
)
from app.dtos.importacao_dto import (
    ImportacaoArquivoResponse,
    ImportacaoProcessadaResponse,
    ProcessarImportacaoRequest,
)
from app.exceptions import ImportacaoInvalidaException
from app.services.autorizacao_service import (
    UsuarioAutenticado,
    exigir_administrador,
)

router = APIRouter(prefix="/administracao", tags=["Administração"])


def obter_administrador(
    usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado),
) -> UsuarioAutenticado:
    exigir_administrador(usuario)
    return usuario


def _resposta_processamento(resultado) -> ImportacaoProcessadaResponse:
    return ImportacaoProcessadaResponse(
        importacao_id=resultado.importacao_id,
        caminho_storage=resultado.caminho_storage,
        mes_referencia=resultado.mes_referencia,
        linhas_lidas=resultado.linhas_lidas,
        linhas_importadas=resultado.linhas_importadas,
        registros_sincronizados=resultado.registros_sincronizados,
        status=resultado.status,
    )


@router.get("/importacoes", response_model=list[ImportacaoArquivoResponse])
def consultar_importacoes(
    limite: int = Query(default=20, ge=1, le=100),
    _: UsuarioAutenticado = Depends(obter_administrador),
) -> list[dict]:
    return listar_importacoes(limite)


@router.post(
    "/importacoes/upload",
    response_model=ImportacaoProcessadaResponse,
    status_code=status.HTTP_201_CREATED,
)
def enviar_e_processar_importacao(
    conteudo: bytes = Body(..., media_type="text/csv"),
    x_file_name: str | None = Header(default=None),
    _: UsuarioAutenticado = Depends(obter_administrador),
) -> ImportacaoProcessadaResponse:
    if not x_file_name:
        raise ImportacaoInvalidaException("O nome do arquivo não foi informado.")
    return _resposta_processamento(processar_upload_csv(x_file_name, conteudo))


@router.post(
    "/importacoes/processar",
    response_model=ImportacaoProcessadaResponse,
    status_code=status.HTTP_201_CREATED,
)
def processar_importacao_ja_enviada(
    dados: ProcessarImportacaoRequest,
    _: UsuarioAutenticado = Depends(obter_administrador),
) -> ImportacaoProcessadaResponse:
    return _resposta_processamento(processar_importacao_storage(dados.caminho_storage))
