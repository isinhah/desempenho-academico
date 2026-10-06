"""Funções de auditoria dos valores calculados da aplicação."""

from sqlalchemy.orm import Session

from app.models import LogAuditoria


def registrar_auditoria(
    db: Session,
    curso_id: int,
    valor_antigo: float,
    valor_novo: float,
    campo: str = "score",
) -> bool:
    """Agenda um log somente quando o valor calculado realmente foi alterado."""
    if valor_antigo == valor_novo:
        return False

    db.add(
        LogAuditoria(
            curso_id=curso_id,
            campo=campo,
            valor_anterior=valor_antigo,
            valor_novo=valor_novo,
        )
    )
    return True
