from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class UsuarioAtualResponse(BaseModel):
    id: UUID
    nome: str
    papel: Literal["DECANO", "COORDENADOR_CURSO", "ADMINISTRADOR"]
    cursos_ids: list[int]
