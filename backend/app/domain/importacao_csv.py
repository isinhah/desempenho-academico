import csv
import io
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database import engine
from app.domain.sincronizar_dados_cursos import executar_etl_importacao
from app.exceptions import (
    ImportacaoDuplicadaException,
    ImportacaoInvalidaException,
    StorageUnavailableException,
)

COLUNAS_ESPERADAS = (
    "escola",
    "curso",
    "alunos_ativos",
    "alunos_evadidos",
    "mes_referencia",
)
CURSOS_POR_ARQUIVO = 72
PADRAO_NOME_ARQUIVO = re.compile(r"^cursos_(\d{4})-(\d{2})\.csv$")
LIMITE_BYTES_ARQUIVO = 1_000_000


@dataclass(frozen=True)
class DadosImportacao:
    caminho_storage: str
    nome_arquivo: str
    mes_referencia: date
    registros: list[dict[str, object]]


@dataclass(frozen=True)
class ResultadoImportacao:
    importacao_id: int
    caminho_storage: str
    mes_referencia: date
    linhas_lidas: int
    linhas_importadas: int
    registros_sincronizados: int
    status: str


def _inteiro(valor: str | None, coluna: str, linha: int) -> int:
    try:
        return int(valor or "")
    except ValueError as error:
        raise ImportacaoInvalidaException(
            f"Linha {linha}: {coluna} deve ser um número inteiro."
        ) from error


def _validar_caminho(caminho_storage: str) -> str:
    caminho = caminho_storage.strip().lstrip("/")
    partes = PurePosixPath(caminho).parts
    if not caminho or ".." in partes or caminho.endswith("/"):
        raise ImportacaoInvalidaException("Caminho do arquivo no Storage inválido.")
    return caminho


def _mes_no_nome(nome_arquivo: str) -> date:
    correspondencia = PADRAO_NOME_ARQUIVO.fullmatch(nome_arquivo)
    if not correspondencia:
        raise ImportacaoInvalidaException(
            "O arquivo deve usar o formato cursos_YYYY-MM.csv."
        )
    try:
        return date(int(correspondencia.group(1)), int(correspondencia.group(2)), 1)
    except ValueError as error:
        raise ImportacaoInvalidaException("Mês inválido no nome do arquivo.") from error


def validar_csv_mensal(conteudo: bytes, caminho_storage: str) -> DadosImportacao:
    caminho = _validar_caminho(caminho_storage)
    nome_arquivo = PurePosixPath(caminho).name
    mes_no_nome = _mes_no_nome(nome_arquivo)
    try:
        texto_csv = conteudo.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ImportacaoInvalidaException("O CSV deve estar codificado em UTF-8.") from error

    leitor = csv.DictReader(io.StringIO(texto_csv))
    if tuple(leitor.fieldnames or ()) != COLUNAS_ESPERADAS:
        raise ImportacaoInvalidaException(
            "Cabeçalhos inválidos. Esperado: " + ", ".join(COLUNAS_ESPERADAS)
        )

    registros: list[dict[str, object]] = []
    cursos_encontrados: set[tuple[str, str]] = set()
    for numero_linha, linha in enumerate(leitor, start=2):
        escola = (linha["escola"] or "").strip()
        curso = (linha["curso"] or "").strip()
        if not escola or not curso:
            raise ImportacaoInvalidaException(
                f"Linha {numero_linha}: escola e curso devem ser preenchidos."
            )
        try:
            mes_referencia = date.fromisoformat(linha["mes_referencia"] or "")
        except ValueError as error:
            raise ImportacaoInvalidaException(
                f"Linha {numero_linha}: mes_referencia deve usar YYYY-MM-DD."
            ) from error
        if mes_referencia != mes_no_nome:
            raise ImportacaoInvalidaException(
                f"Linha {numero_linha}: mes_referencia deve ser {mes_no_nome.isoformat()}."
            )

        alunos_ativos = _inteiro(linha["alunos_ativos"], "alunos_ativos", numero_linha)
        alunos_evadidos = _inteiro(
            linha["alunos_evadidos"], "alunos_evadidos", numero_linha
        )
        if alunos_ativos <= 0:
            raise ImportacaoInvalidaException(
                f"Linha {numero_linha}: alunos_ativos deve ser maior que zero."
            )
        if alunos_evadidos < 0 or alunos_evadidos > alunos_ativos:
            raise ImportacaoInvalidaException(
                f"Linha {numero_linha}: alunos_evadidos deve estar entre zero e alunos_ativos."
            )
        chave = (escola, curso)
        if chave in cursos_encontrados:
            raise ImportacaoInvalidaException(
                f"Linha {numero_linha}: curso duplicado no arquivo mensal."
            )
        cursos_encontrados.add(chave)
        registros.append(
            {
                "escola": escola,
                "curso": curso,
                "alunos_ativos": alunos_ativos,
                "alunos_evadidos": alunos_evadidos,
                "mes_referencia": mes_referencia,
            }
        )

    if len(registros) != CURSOS_POR_ARQUIVO:
        raise ImportacaoInvalidaException(
            f"O arquivo deve conter {CURSOS_POR_ARQUIVO} cursos; recebeu {len(registros)}."
        )
    return DadosImportacao(caminho, nome_arquivo, mes_no_nome, registros)


def _baixar_do_storage(caminho_storage: str) -> bytes:
    url_supabase = os.getenv("SUPABASE_URL", "").rstrip("/")
    chave_servico = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "importacoes-cursos")
    if not url_supabase or not chave_servico:
        raise StorageUnavailableException(
            "SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY devem ser configurados no backend."
        )

    url = (
        f"{url_supabase}/storage/v1/object/{quote(bucket, safe='')}/"
        f"{quote(caminho_storage, safe='/')}"
    )
    requisicao = Request(
        url,
        headers={"apikey": chave_servico, "Authorization": f"Bearer {chave_servico}"},
    )
    try:
        with urlopen(requisicao, timeout=20) as resposta:  # noqa: S310
            conteudo = resposta.read(LIMITE_BYTES_ARQUIVO + 1)
    except HTTPError as error:
        raise StorageUnavailableException(
            f"Não foi possível baixar o arquivo do Storage (HTTP {error.code})."
        ) from error
    except URLError as error:
        raise StorageUnavailableException(
            "Não foi possível conectar ao Supabase Storage."
        ) from error
    if len(conteudo) > LIMITE_BYTES_ARQUIVO:
        raise ImportacaoInvalidaException("O CSV excede o limite de 1 MB.")
    return conteudo


def _registrar_importacao(dados: DadosImportacao) -> int:
    try:
        with engine.begin() as conexao:
            existente = conexao.execute(
                text(
                    "SELECT id FROM importacao_arquivo "
                    "WHERE caminho_storage = :caminho_storage"
                ),
                {"caminho_storage": dados.caminho_storage},
            ).scalar_one_or_none()
            if existente is not None:
                raise ImportacaoDuplicadaException(
                    "Este arquivo já foi processado. Use um novo caminho para uma correção."
                )

            importacao_id = conexao.execute(
                text(
                    "INSERT INTO importacao_arquivo "
                    "(caminho_storage, nome_arquivo, mes_referencia, status, linhas_lidas) "
                    "VALUES (:caminho_storage, :nome_arquivo, :mes_referencia, "
                    "'PROCESSANDO', :linhas_lidas) RETURNING id"
                ),
                {
                    "caminho_storage": dados.caminho_storage,
                    "nome_arquivo": dados.nome_arquivo,
                    "mes_referencia": dados.mes_referencia,
                    "linhas_lidas": len(dados.registros),
                },
            ).scalar_one()
            conexao.execute(
                text(
                    "INSERT INTO curso_indicador_bruto "
                    "(importacao_id, escola, curso, alunos_ativos, alunos_evadidos, mes_referencia) "
                    "VALUES (:importacao_id, :escola, :curso, :alunos_ativos, "
                    ":alunos_evadidos, :mes_referencia) "
                    "ON CONFLICT (escola, curso, mes_referencia) DO UPDATE SET "
                    "importacao_id = EXCLUDED.importacao_id, "
                    "alunos_ativos = EXCLUDED.alunos_ativos, "
                    "alunos_evadidos = EXCLUDED.alunos_evadidos"
                ),
                [{"importacao_id": importacao_id, **registro} for registro in dados.registros],
            )
            return int(importacao_id)
    except IntegrityError as error:
        raise ImportacaoInvalidaException(
            "Não foi possível registrar os dados brutos da importação."
        ) from error
    except SQLAlchemyError as error:
        raise RuntimeError("Não foi possível registrar a importação no banco.") from error


def _atualizar_status(
    importacao_id: int, status: str, linhas_importadas: int = 0, mensagem_erro: str | None = None
) -> None:
    with engine.begin() as conexao:
        conexao.execute(
            text(
                "UPDATE importacao_arquivo SET status = :status, "
                "linhas_importadas = :linhas_importadas, mensagem_erro = :mensagem_erro, "
                "processado_em = CURRENT_TIMESTAMP WHERE id = :importacao_id"
            ),
            {
                "importacao_id": importacao_id,
                "status": status,
                "linhas_importadas": linhas_importadas,
                "mensagem_erro": mensagem_erro,
            },
        )


def processar_importacao_storage(caminho_storage: str) -> ResultadoImportacao:
    caminho = _validar_caminho(caminho_storage)
    dados = validar_csv_mensal(_baixar_do_storage(caminho), caminho)
    importacao_id = _registrar_importacao(dados)
    try:
        registros_sincronizados = executar_etl_importacao(importacao_id)
    except Exception as error:
        _atualizar_status(importacao_id, "FALHA", mensagem_erro=str(error))
        raise

    _atualizar_status(importacao_id, "CONCLUIDA", len(dados.registros))
    return ResultadoImportacao(
        importacao_id=importacao_id,
        caminho_storage=dados.caminho_storage,
        mes_referencia=dados.mes_referencia,
        linhas_lidas=len(dados.registros),
        linhas_importadas=len(dados.registros),
        registros_sincronizados=registros_sincronizados,
        status="CONCLUIDA",
    )
