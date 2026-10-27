import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.dtos.error_dto import ErrorResponse, ValidationErrorDetail
from app.exceptions import ApplicationException

logger = logging.getLogger(__name__)


def _response(
    status: int,
    code: str,
    message: str,
    details: list[ValidationErrorDetail] | None = None,
) -> JSONResponse:
    body = ErrorResponse(
        status=status,
        codigo=code,
        mensagem=message,
        detalhes=details or [],
    )
    return JSONResponse(status_code=status, content=body.model_dump(mode="json"))


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        _: Request, exception: ApplicationException
    ) -> JSONResponse:
        return _response(exception.status_code, exception.code, exception.message)

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        _: Request, exception: RequestValidationError
    ) -> JSONResponse:
        details = [
            ValidationErrorDetail(
                campo=".".join(str(item) for item in error["loc"] if item != "body"),
                mensagem=error["msg"],
                tipo=error["type"],
            )
            for error in exception.errors()
        ]
        return _response(
            422,
            "dados_invalidos",
            "Os dados enviados são inválidos.",
            details,
        )

    @app.exception_handler(OperationalError)
    async def database_unavailable_exception_handler(
        _: Request, exception: OperationalError
    ) -> JSONResponse:
        logger.warning("Banco de dados indisponível: %s", exception.orig)
        return _response(
            503,
            "banco_indisponivel",
            "Banco de dados indisponível.",
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _: Request, exception: StarletteHTTPException
    ) -> JSONResponse:
        codes = {404: "recurso_nao_encontrado", 405: "metodo_nao_permitido"}
        return _response(
            exception.status_code,
            codes.get(exception.status_code, "erro_http"),
            str(exception.detail),
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request, exception: Exception
    ) -> JSONResponse:
        logger.exception("Erro não tratado em %s", request.url.path, exc_info=exception)
        return _response(500, "erro_interno", "Ocorreu um erro interno.")
