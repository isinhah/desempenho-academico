import logging
import os
from datetime import date

from app.database import SessionLocal
from app.domain.relatorio_mensal import gerar_relatorio_mensal, montar_email
from app.messaging import FILA_ENVIAR_RELATORIO, FILA_GERAR_RELATORIO, consumir, publicar

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def processar(mensagem: dict[str, str]) -> None:
    mes_referencia = date.fromisoformat(mensagem["mes_referencia"])
    destinatario = os.getenv("COORDINATOR_EMAIL")
    if not destinatario:
        raise RuntimeError("COORDINATOR_EMAIL não foi definido.")

    with SessionLocal() as db:
        relatorio = gerar_relatorio_mensal(db, mes_referencia)
    email = montar_email(relatorio)
    publicar(FILA_ENVIAR_RELATORIO, {"para": destinatario, **email})
    logger.info("Relatório de %s enviado para a fila de e-mail.", mes_referencia)


if __name__ == "__main__":
    consumir(FILA_GERAR_RELATORIO, processar)
