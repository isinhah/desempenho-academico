import os
from functools import lru_cache
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError, PyJWKClient
from jwt.exceptions import PyJWKClientError
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import AuthenticationException
from app.services.autorizacao_service import AutorizacaoService, UsuarioAutenticado

bearer_scheme = HTTPBearer(auto_error=False)


def _supabase_url() -> str:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    if not url:
        raise AuthenticationException("A autenticação não está configurada no servidor.")
    return url


@lru_cache
def _jwks_client(issuer: str) -> PyJWKClient:
    return PyJWKClient(f"{issuer}/.well-known/jwks.json", cache_keys=True)


def _validar_token(token: str) -> UUID:
    issuer = f"{_supabase_url()}/auth/v1"

    try:
        algoritmo = jwt.get_unverified_header(token).get("alg")
        if algoritmo == "HS256":
            segredo = os.getenv("SUPABASE_JWT_SECRET")
            if not segredo:
                raise AuthenticationException(
                    "JWT HS256 requer SUPABASE_JWT_SECRET no servidor."
                )
            chave = segredo
        elif algoritmo in {"RS256", "ES256"}:
            chave = _jwks_client(issuer).get_signing_key_from_jwt(token).key
        else:
            raise AuthenticationException("Token com algoritmo não permitido.")

        payload = jwt.decode(
            token,
            chave,
            algorithms=[algoritmo],
            audience="authenticated",
            issuer=issuer,
        )
        return UUID(payload["sub"])
    except (InvalidTokenError, PyJWKClientError, KeyError, ValueError) as error:
        raise AuthenticationException("Token de acesso inválido ou expirado.") from error


def obter_usuario_autenticado(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UsuarioAutenticado:
    if credenciais is None or credenciais.scheme.lower() != "bearer":
        raise AuthenticationException("Token de acesso não informado.")

    usuario_id = _validar_token(credenciais.credentials)
    return AutorizacaoService(db).obter_usuario(usuario_id)
