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
