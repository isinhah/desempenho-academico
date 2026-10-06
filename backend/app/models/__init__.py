"""Modelos ORM expostos pelo pacote."""

from app.models.curso_model import Curso, HistoricoIndicador
from app.models.escola_model import Escola
from app.models.log_auditoria_model import LogAuditoria

__all__ = ["Curso", "Escola", "HistoricoIndicador", "LogAuditoria"]
