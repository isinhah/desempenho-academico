import logging
import os
import time
from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.domain.relatorio_mensal import mes_anterior
from app.messaging import FILA_GERAR_RELATORIO, publicar

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def _agora() -> datetime:
    timezone = ZoneInfo(os.getenv("REPORT_TIMEZONE", "America/Sao_Paulo"))
    return datetime.now(timezone)


def _periodo_referencia(data_atual: date) -> date:
    return mes_anterior(date(data_atual.year, data_atual.month, 1))


def _publicar_relatorio(periodo: date) -> None:
    publicar(FILA_GERAR_RELATORIO, {"mes_referencia": periodo.isoformat()})
    logger.info("Solicitação de relatório publicada para %s.", periodo.isoformat())


def executar() -> None:
    """Executa o agendamento no dia e hora configurados no ambiente."""
    dia = int(os.getenv("REPORT_SCHEDULE_DAY", "1"))
    hora = int(os.getenv("REPORT_SCHEDULE_HOUR", "8"))
    executar_ao_iniciar = os.getenv("REPORT_RUN_ON_STARTUP", "false").lower() == "true"
    ultimo_periodo_publicado: date | None = None

    if executar_ao_iniciar:
        agora = _agora()
        periodo = _periodo_referencia(agora.date())
        _publicar_relatorio(periodo)
        ultimo_periodo_publicado = periodo

    while True:
        agora = _agora()
        periodo = _periodo_referencia(agora.date())
        if (
            agora.day == dia
            and agora.hour >= hora
            and ultimo_periodo_publicado != periodo
        ):
            _publicar_relatorio(periodo)
            ultimo_periodo_publicado = periodo
        time.sleep(30)


if __name__ == "__main__":
    executar()
