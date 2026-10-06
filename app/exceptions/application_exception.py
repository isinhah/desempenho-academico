"""Exceções independentes do transporte HTTP usadas pela camada de negócio."""


class ApplicationException(Exception):
    status_code = 400
    code = "erro_de_negocio"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ResourceNotFoundException(ApplicationException):
    status_code = 404
    code = "recurso_nao_encontrado"


class ConflictException(ApplicationException):
    status_code = 409
    code = "conflito"


class BusinessRuleException(ApplicationException):
    status_code = 422
    code = "regra_de_negocio_invalida"


class DatabaseUnavailableException(ApplicationException):
    status_code = 503
    code = "banco_indisponivel"
