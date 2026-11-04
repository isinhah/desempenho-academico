from datetime import date, datetime

from pydantic import BaseModel, Field


class ProcessarImportacaoRequest(BaseModel):
    caminho_storage: str = Field(min_length=1, max_length=500)


class ImportacaoProcessadaResponse(BaseModel):
    importacao_id: int
    caminho_storage: str
    mes_referencia: date
    linhas_lidas: int
    linhas_importadas: int
    registros_sincronizados: int
    status: str


class ImportacaoArquivoResponse(BaseModel):
    id: int
    caminho_storage: str
    nome_arquivo: str
    mes_referencia: date
    status: str
    linhas_lidas: int
    linhas_importadas: int
    linhas_rejeitadas: int
    mensagem_erro: str | None = None
    criado_em: datetime
    processado_em: datetime | None = None
