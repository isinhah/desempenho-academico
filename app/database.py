"""Configuração compartilhada de acesso ao banco de dados."""

import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# O .env continua na raiz do projeto, um nível acima de app/.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL não foi definida no arquivo .env.")

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Classe-base de todos os modelos SQLAlchemy do projeto."""


def get_db() -> Generator[Session, None, None]:
    """Entrega uma sessão por requisição e sempre a fecha ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
