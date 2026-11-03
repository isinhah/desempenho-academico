from datetime import date

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
