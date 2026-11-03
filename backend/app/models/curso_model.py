from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.escola_model import Escola


class Curso(Base):
    __tablename__ = "curso"
    __table_args__ = (
        UniqueConstraint("escola_id", "nome", name="uq_curso_escola_nome"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    escola_id: Mapped[int] = mapped_column(ForeignKey("escola.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    alunos_ativos: Mapped[int] = mapped_column(Integer, nullable=False)
    alunos_evadidos: Mapped[int] = mapped_column(Integer, nullable=False)
    resumo_academico: Mapped[str | None] = mapped_column(Text, nullable=True)
    resumo_referencia: Mapped[date | None] = mapped_column(Date, nullable=True)
    resumo_atualizado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    escola: Mapped[Escola] = relationship(back_populates="cursos")
    historicos: Mapped[list[HistoricoIndicador]] = relationship(
        back_populates="curso", cascade="all, delete-orphan"
    )


class HistoricoIndicador(Base):
    __tablename__ = "historico_indicador"
    __table_args__ = (
        UniqueConstraint(
            "curso_id", "mes_referencia", name="uq_historico_curso_mes_referencia"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    curso_id: Mapped[int] = mapped_column(ForeignKey("curso.id"), nullable=False)
    mes_referencia: Mapped[date] = mapped_column(Date, nullable=False)
    pct_evasao: Mapped[float] = mapped_column(Float, nullable=False)

    curso: Mapped[Curso] = relationship(back_populates="historicos")
