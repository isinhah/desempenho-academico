"""API do mini-portfólio."""

from contextlib import asynccontextmanager
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv(Path(__file__).with_name(".env"))

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL não foi definida no arquivo .env.")

engine = create_engine(database_url, pool_pre_ping=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Valida a conexão antes de a API começar a receber requisições."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise RuntimeError("Não foi possível conectar ao banco de dados.") from error

    yield
    engine.dispose()


app = FastAPI(title="Mini Portfólio API", lifespan=lifespan)


@app.get("/")
def inicio():
    return {"mensagem": "Mini Portfólio API está no ar."}


@app.get("/health/database")
def health_database():
    """Confirma que a API consegue consultar o PostgreSQL configurado."""
    try:
        with engine.connect() as connection:
            database, user = connection.execute(
                text("SELECT current_database(), current_user")
            ).one()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponível.",
        ) from error

    return {"status": "ok", "database": database, "user": user}
