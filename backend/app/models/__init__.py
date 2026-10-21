"""Modelos ORM expostos pelo pacote."""

from app.models.curso_model import Curso, HistoricoIndicador
from app.models.escola_model import Escola

__all__ = ["Curso", "Escola", "HistoricoIndicador"]
