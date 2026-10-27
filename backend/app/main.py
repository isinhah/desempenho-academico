import asyncio
from contextlib import asynccontextmanager

from app.controllers.admin_controller import router as admin_router
from app.controllers.curso_controller import router as curso_router
from app.controllers.escola_controller import router as escola_router
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.database import Base, engine
from app.exceptions import DatabaseUnavailableException
from app.handlers.exception_handler import register_exception_handlers


@asynccontextmanager
async def lifespan(_: FastAPI):
    for tentativa in range(10):
        try:
            Base.metadata.create_all(bind=engine, checkfirst=True)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            break
        except SQLAlchemyError as error:
            if tentativa == 9:
                raise RuntimeError("Não foi possível conectar ao banco de dados.") from error
            await asyncio.sleep(1)

    yield
    engine.dispose()


app = FastAPI(title="Mini Portfólio API", lifespan=lifespan)
register_exception_handlers(app)
app.include_router(curso_router)
app.include_router(escola_router)
app.include_router(admin_router)


@app.get("/")
def inicio():
    return {"mensagem": "Mini Portfólio API está no ar."}


@app.get("/health/database")
def health_database():
    try:
        with engine.connect() as connection:
            database, user = connection.execute(
                text("SELECT current_database(), current_user")
            ).one()
    except SQLAlchemyError as error:
        raise DatabaseUnavailableException("Banco de dados indisponível.") from error

    return {"status": "ok", "database": database, "user": user}
