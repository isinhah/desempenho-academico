class ApplicationException(Exception):
    status_code = 400
    code = "erro_de_negocio"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ResourceNotFoundException(ApplicationException):
    status_code = 404
    code = "recurso_nao_encontrado"


class DatabaseUnavailableException(ApplicationException):
    status_code = 503
    code = "banco_indisponivel"


class AuthenticationException(ApplicationException):
    status_code = 401
    code = "nao_autenticado"


class AuthorizationException(ApplicationException):
    status_code = 403
    code = "acesso_negado"


class ImportacaoInvalidaException(ApplicationException):
    status_code = 422
    code = "importacao_invalida"


class ImportacaoDuplicadaException(ApplicationException):
    status_code = 409
    code = "importacao_duplicada"


class StorageUnavailableException(ApplicationException):
    status_code = 502
    code = "storage_indisponivel"
