from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LogAuditoria(Base):
    """Registro imutável de alterações nos valores calculados de um curso."""

    __tablename__ = "log_auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    curso_id: Mapped[int] = mapped_column(ForeignKey("curso.id"), nullable=False)
    campo: Mapped[str] = mapped_column(String(50), nullable=False, default="score")
    valor_anterior: Mapped[float] = mapped_column("valor_antigo", Float, nullable=False)
    valor_novo: Mapped[float] = mapped_column(Float, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        "data_hora", DateTime, nullable=False, server_default=func.now()
    )
