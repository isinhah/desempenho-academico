from datetime import date

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.domain.resumo_academico import gerar_resumo_academico


def calcular_pct_evasao(alunos_ativos: int, alunos_evadidos: int) -> float:
    return 0.0 if alunos_ativos == 0 else round((alunos_evadidos / alunos_ativos) * 100, 2)


def _validar_registro(registro: dict) -> dict:
    escola = str(registro["escola"] or "").strip()
    curso = str(registro["curso"] or "").strip()
    alunos_ativos = registro["alunos_ativos"]
    alunos_evadidos = registro["alunos_evadidos"]
    mes_referencia = registro["mes_referencia"]

    if not escola or not curso:
        raise ValueError("escola e curso devem ser preenchidos.")
    if not isinstance(alunos_ativos, int) or not isinstance(alunos_evadidos, int):
        raise ValueError("alunos_ativos e alunos_evadidos devem ser números inteiros.")
    if alunos_ativos < 0 or alunos_evadidos < 0:
        raise ValueError("alunos_ativos e alunos_evadidos não podem ser negativos.")
    if alunos_evadidos > alunos_ativos:
        raise ValueError("alunos_evadidos não pode ser maior que alunos_ativos.")
    if not isinstance(mes_referencia, date):
        raise ValueError("mes_referencia deve ser uma data válida.")

    return {
        "escola": escola,
        "curso": curso,
        "alunos_ativos": alunos_ativos,
        "alunos_evadidos": alunos_evadidos,
        "mes_referencia": mes_referencia,
    }


def _sincronizar_registros(registros: list[dict]) -> int:
    if not registros:
        print("Nenhum registro encontrado para sincronizar.")
        return 0

    try:
        with engine.begin() as conexao:
            print(f"Validando e sincronizando {len(registros)} registros...", flush=True)
            escolas_existentes = {
                escola["nome"]: escola["id"]
                for escola in conexao.execute(text("SELECT id, nome FROM escola")).mappings()
            }
            nomes_escolas = {registro["escola"] for registro in registros}
            escolas_novas = [
                {"nome": nome} for nome in nomes_escolas if nome not in escolas_existentes
            ]
            if escolas_novas:
                conexao.execute(text("INSERT INTO escola (nome) VALUES (:nome)"), escolas_novas)
                escolas_existentes = {
                    escola["nome"]: escola["id"]
                    for escola in conexao.execute(text("SELECT id, nome FROM escola")).mappings()
                }

            cursos_por_chave = {
                (curso["escola_id"], curso["nome"]): curso["id"]
                for curso in conexao.execute(
                    text("SELECT id, escola_id, nome FROM curso")
                ).mappings()
            }
            dados_atuais: dict[tuple[int, str], dict] = {}
            for registro in registros:
                chave = (escolas_existentes[registro["escola"]], registro["curso"])
                dados_atuais[chave] = registro

            cursos_novos = [
                {
                    "escola_id": escola_id,
                    "nome": nome,
                    "alunos_ativos": registro["alunos_ativos"],
                    "alunos_evadidos": registro["alunos_evadidos"],
                }
                for (escola_id, nome), registro in dados_atuais.items()
                if (escola_id, nome) not in cursos_por_chave
            ]
            if cursos_novos:
                conexao.execute(
                    text(
                        "INSERT INTO curso (escola_id, nome, alunos_ativos, alunos_evadidos) "
                        "VALUES (:escola_id, :nome, :alunos_ativos, :alunos_evadidos)"
                    ),
                    cursos_novos,
                )
                cursos_por_chave = {
                    (curso["escola_id"], curso["nome"]): curso["id"]
                    for curso in conexao.execute(
                        text("SELECT id, escola_id, nome FROM curso")
                    ).mappings()
                }

            conexao.execute(
                text(
                    "UPDATE curso SET alunos_ativos = :alunos_ativos, "
                    "alunos_evadidos = :alunos_evadidos WHERE id = :curso_id"
                ),
                [
                    {
                        "curso_id": cursos_por_chave[chave],
                        "alunos_ativos": registro["alunos_ativos"],
                        "alunos_evadidos": registro["alunos_evadidos"],
                    }
                    for chave, registro in dados_atuais.items()
                ],
            )

            historicos_existentes = {
                (historico["curso_id"], historico["mes_referencia"]): historico["id"]
                for historico in conexao.execute(
                    text("SELECT id, curso_id, mes_referencia FROM historico_indicador")
                ).mappings()
            }
            print("Sincronizando o histórico de evasão...", flush=True)
            historicos_novos = []
            historicos_atualizados = []
            for registro in registros:
                curso_id = cursos_por_chave[
                    (escolas_existentes[registro["escola"]], registro["curso"])
                ]
                dados_historico = {
                    "curso_id": curso_id,
                    "mes_referencia": registro["mes_referencia"],
                    "pct_evasao": calcular_pct_evasao(
                        registro["alunos_ativos"], registro["alunos_evadidos"]
                    ),
                }
                historico_id = historicos_existentes.get(
                    (curso_id, registro["mes_referencia"])
                )
                if historico_id is None:
                    historicos_novos.append(dados_historico)
                else:
                    historicos_atualizados.append(
                        {"historico_id": historico_id, **dados_historico}
                    )

            if historicos_novos:
                conexao.execute(
                    text(
                        "INSERT INTO historico_indicador "
                        "(curso_id, mes_referencia, pct_evasao) "
                        "VALUES (:curso_id, :mes_referencia, :pct_evasao)"
                    ),
                    historicos_novos,
                )
            if historicos_atualizados:
                conexao.execute(
                    text(
                        "UPDATE historico_indicador SET pct_evasao = :pct_evasao "
                        "WHERE id = :historico_id"
                    ),
                    historicos_atualizados,
                )

            print("Atualizando resumos acadêmicos dos cursos...", flush=True)
            cursos_sincronizados = set(cursos_por_chave[chave] for chave in dados_atuais)
            historicos_por_curso = {curso_id: [] for curso_id in cursos_sincronizados}
            for historico in conexao.execute(
                text(
                    "SELECT curso_id, mes_referencia, pct_evasao "
                    "FROM historico_indicador ORDER BY curso_id, mes_referencia"
                )
            ).mappings():
                if historico["curso_id"] in historicos_por_curso:
                    historicos_por_curso[historico["curso_id"]].append(
                        (historico["mes_referencia"], float(historico["pct_evasao"]))
                    )

            resumos = [
                {
                    "curso_id": curso_id,
                    "resumo_academico": gerar_resumo_academico(historico),
                    "resumo_referencia": historico[-1][0],
                }
                for curso_id, historico in historicos_por_curso.items()
                if historico
            ]
            if resumos:
                conexao.execute(
                    text(
                        "UPDATE curso SET resumo_academico = :resumo_academico, "
                        "resumo_referencia = :resumo_referencia, "
                        "resumo_atualizado_em = CURRENT_TIMESTAMP "
                        "WHERE id = :curso_id"
                    ),
                    resumos,
                )
    except SQLAlchemyError as error:
        raise RuntimeError(
            "Não foi possível sincronizar os dados. Confirme a conexão e a estrutura do banco."
        ) from error

    print(f"ETL concluído: {len(registros)} registro(s) sincronizado(s).")
    return len(registros)


def _ler_registros_importacao(importacao_id: int) -> list[dict]:
    with engine.connect() as conexao:
        return [
            _validar_registro(dict(registro))
            for registro in conexao.execute(
                text(
                    "SELECT escola, curso, alunos_ativos, alunos_evadidos, mes_referencia "
                    "FROM curso_indicador_bruto WHERE importacao_id = :importacao_id "
                    "ORDER BY escola, curso"
                ),
                {"importacao_id": importacao_id},
            ).mappings()
        ]


def executar_etl_importacao(importacao_id: int) -> int:
    print(f"Lendo dados da importação {importacao_id}...", flush=True)
    registros = _ler_registros_importacao(importacao_id)
    return _sincronizar_registros(registros)
