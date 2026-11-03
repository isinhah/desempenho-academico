from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.exceptions import AuthenticationException, AuthorizationException


@dataclass(frozen=True)
class UsuarioAutenticado:
    id: UUID
    nome: str
    papel: str
    cursos_ids: tuple[int, ...]

    @property
    def e_decano(self) -> bool:
        return self.papel == "DECANO"

    def pode_acessar_curso(self, curso_id: int) -> bool:
        return self.e_decano or curso_id in self.cursos_ids


class AutorizacaoService:
    def __init__(self, db: Session):
        self.db = db

    def obter_usuario(self, usuario_id: UUID) -> UsuarioAutenticado:
        registro = self.db.execute(
            text(
                """
                SELECT
                    perfil.id,
                    perfil.nome,
                    perfil.papel,
                    COALESCE(
                        array_agg(vinculo.curso_id) FILTER (WHERE vinculo.curso_id IS NOT NULL),
                        ARRAY[]::INTEGER[]
                    ) AS cursos_ids
                FROM public.perfil_usuario AS perfil
                LEFT JOIN public.usuario_curso AS vinculo ON vinculo.usuario_id = perfil.id
                WHERE perfil.id = :usuario_id
                  AND perfil.ativo = TRUE
                GROUP BY perfil.id, perfil.nome, perfil.papel
                """
            ),
            {"usuario_id": str(usuario_id)},
        ).mappings().one_or_none()

        if registro is None:
            raise AuthenticationException("Usuário sem perfil de acesso ativo.")

        return UsuarioAutenticado(
            id=registro["id"],
            nome=registro["nome"],
            papel=registro["papel"],
            cursos_ids=tuple(registro["cursos_ids"]),
        )


def exigir_visao_geral(usuario: UsuarioAutenticado) -> None:
    if not usuario.e_decano:
        raise AuthorizationException("Seu perfil não possui acesso à visão geral.")


def exigir_acesso_ao_curso(usuario: UsuarioAutenticado, curso_id: int) -> None:
    if not usuario.pode_acessar_curso(curso_id):
        raise AuthorizationException("Você não possui acesso a este curso.")
