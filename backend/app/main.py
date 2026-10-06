"""API do mini-portfólio."""

from contextlib import asynccontextmanager

from app.controllers.curso_controller import router as curso_router
from app.controllers.escola_controller import router as escola_router
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.database import engine
from app.exceptions import DatabaseUnavailableException
from app.handlers.exception_handler import register_exception_handlers
from app.models import LogAuditoria


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Valida a conexão antes de a API começar a receber requisições."""
    try:
        LogAuditoria.__table__.create(bind=engine, checkfirst=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise RuntimeError("Não foi possível conectar ao banco de dados.") from error

    yield
    engine.dispose()


app = FastAPI(title="Mini Portfólio API", lifespan=lifespan)
register_exception_handlers(app)
app.include_router(curso_router)
app.include_router(escola_router)


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
        raise DatabaseUnavailableException("Banco de dados indisponível.") from error

    return {"status": "ok", "database": database, "user": user}
