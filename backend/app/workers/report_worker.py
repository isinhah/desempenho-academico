import logging
import os
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.domain.relatorio_mensal import (
    gerar_relatorio_decano,
    gerar_resumo_coordenador,
    montar_email_coordenador,
    montar_email_decano,
)
from app.messaging import FILA_ENVIAR_RELATORIO, FILA_GERAR_RELATORIO, consumir, publicar

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DestinatarioRelatorio:
    id: UUID
    nome: str
    papel: str
    email: str
    cursos_ids: tuple[int, ...]


def _listar_destinatarios(db: Session) -> list[DestinatarioRelatorio]:
    registros = db.execute(
        text(
            """
            SELECT
                perfil.id,
                perfil.nome,
                perfil.papel,
                usuario.email,
                COALESCE(
                    array_agg(vinculo.curso_id) FILTER (WHERE vinculo.curso_id IS NOT NULL),
                    ARRAY[]::INTEGER[]
                ) AS cursos_ids
            FROM public.perfil_usuario AS perfil
            JOIN auth.users AS usuario ON usuario.id = perfil.id
            LEFT JOIN public.usuario_curso AS vinculo ON vinculo.usuario_id = perfil.id
            WHERE perfil.ativo = TRUE
              AND usuario.email IS NOT NULL
            GROUP BY perfil.id, perfil.nome, perfil.papel, usuario.email
            ORDER BY perfil.nome
            """
        )
    ).mappings().all()
    return [
        DestinatarioRelatorio(
            id=registro["id"],
            nome=registro["nome"],
            papel=registro["papel"],
            email=registro["email"],
            cursos_ids=tuple(registro["cursos_ids"]),
        )
        for registro in registros
    ]


def _enfileirar_email(destinatario: DestinatarioRelatorio, email: dict[str, str]) -> None:
    publicar(FILA_ENVIAR_RELATORIO, {"para": destinatario.email, **email})


def processar(mensagem: dict[str, str]) -> None:
    mes_referencia = date.fromisoformat(mensagem["mes_referencia"])

    with SessionLocal() as db:
        destinatarios = _listar_destinatarios(db)
        relatorio_decano = None
        enviados = 0

        for destinatario in destinatarios:
            if destinatario.papel == "DECANO":
                if relatorio_decano is None:
                    relatorio_decano = gerar_relatorio_decano(db, mes_referencia)
                email = montar_email_decano(destinatario.nome, relatorio_decano)
            elif destinatario.papel == "COORDENADOR_CURSO":
                if not destinatario.cursos_ids:
                    logger.warning(
                        "Coordenador %s não possui cursos vinculados; relatório não enviado.",
                        destinatario.id,
                    )
                    continue
                resumo = gerar_resumo_coordenador(
                    db, mes_referencia, destinatario.cursos_ids
                )
                email = montar_email_coordenador(destinatario.nome, resumo)
            else:
                logger.warning("Perfil desconhecido para relatório: %s", destinatario.papel)
                continue

            _enfileirar_email(destinatario, email)
            enviados += 1

    logger.info(
        "%s relatório(s) de %s enviado(s) para a fila de e-mail.",
        enviados,
        mes_referencia,
    )


if __name__ == "__main__":
    consumir(FILA_GERAR_RELATORIO, processar)
