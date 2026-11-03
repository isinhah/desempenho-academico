import logging
import os
import smtplib
from email.message import EmailMessage

from app.messaging import FILA_ENVIAR_RELATORIO, consumir

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def processar(mensagem: dict[str, str]) -> None:
    email = EmailMessage()
    email["Subject"] = mensagem["assunto"]
    email["From"] = os.getenv("EMAIL_FROM", "relatorios@faculdade")
    email["To"] = mensagem["para"]
    email.set_content(mensagem["texto"])
    email.add_alternative(mensagem["html"], subtype="html")

    host = os.getenv("SMTP_HOST", "mailpit")
    porta = int(os.getenv("SMTP_PORT", "1025"))
    with smtplib.SMTP(host, porta, timeout=15) as smtp:
        smtp.send_message(email)
    logger.info("Relatório enviado para %s.", mensagem["para"])


if __name__ == "__main__":
    consumir(FILA_ENVIAR_RELATORIO, processar)
