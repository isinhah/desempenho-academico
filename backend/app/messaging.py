import json
import logging
import os
import time
from collections.abc import Callable
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError

logger = logging.getLogger(__name__)

FILA_GERAR_RELATORIO = "report.generate"
FILA_ENVIAR_RELATORIO = "report.send"


def _url_rabbitmq() -> str:
    return os.getenv("RABBITMQ_URL", "amqp://app:app@rabbitmq:5672/%2F")


def _conectar() -> pika.BlockingConnection:
    parametros = pika.URLParameters(_url_rabbitmq())
    parametros.heartbeat = 30
    return pika.BlockingConnection(parametros)


def declarar_filas(canal: BlockingChannel) -> None:
    canal.queue_declare(queue=FILA_GERAR_RELATORIO, durable=True)
    canal.queue_declare(queue=FILA_ENVIAR_RELATORIO, durable=True)


def publicar(fila: str, mensagem: dict[str, Any]) -> None:
    conexao = _conectar()
    try:
        canal = conexao.channel()
        declarar_filas(canal)
        canal.basic_publish(
            exchange="",
            routing_key=fila,
            body=json.dumps(mensagem, ensure_ascii=False),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                content_type="application/json",
            ),
        )
    finally:
        conexao.close()


def consumir(
    fila: str,
    processar: Callable[[dict[str, Any]], None],
) -> None:
    """Consome uma fila."""
    while True:
        try:
            conexao = _conectar()
            canal = conexao.channel()
            declarar_filas(canal)
            canal.basic_qos(prefetch_count=1)

            def callback(
                channel: BlockingChannel,
                method: pika.spec.Basic.Deliver,
                _: pika.spec.BasicProperties,
                body: bytes,
            ) -> None:
                try:
                    processar(json.loads(body))
                except Exception:
                    logger.exception("Falha ao processar a mensagem da fila %s.", fila)
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                else:
                    channel.basic_ack(delivery_tag=method.delivery_tag)

            canal.basic_consume(queue=fila, on_message_callback=callback)
            logger.info("Aguardando mensagens em %s.", fila)
            canal.start_consuming()
        except AMQPConnectionError:
            logger.warning("RabbitMQ indisponível. Nova tentativa em 5 segundos.")
            time.sleep(5)
