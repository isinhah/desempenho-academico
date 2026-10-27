from datetime import date

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine

def calcular_pct_evasao(alunos_ativos: int, alunos_evadidos: int) -> float:
    if alunos_ativos == 0:
        return 0.0
    return round((alunos_evadidos / alunos_ativos) * 100, 2)


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


def executar_etl() -> int:
    try:
        with engine.begin() as conexao:
            print("Lendo dados da tabela cursos...", flush=True)
            origem = conexao.execute(
                text(
                    "SELECT escola, curso, alunos_ativos, alunos_evadidos, mes_referencia "
                    "FROM cursos ORDER BY escola, curso, mes_referencia"
                )
            ).mappings()
            registros = [_validar_registro(dict(registro)) for registro in origem]

            if not registros:
                print("Nenhum registro encontrado na tabela cursos.")
                return 0

            print(f"Validando e sincronizando {len(registros)} registros...", flush=True)
            escolas_existentes = {
                escola["nome"]: escola["id"]
                for escola in conexao.execute(text("SELECT id, nome FROM escola")).mappings()
            }
            nomes_escolas = {registro["escola"] for registro in registros}
            escolas_novas = [
                {"nome": nome}
                for nome in nomes_escolas
                if nome not in escolas_existentes
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
            dados_atuais = {}
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

            cursos_atualizados = [
                {
                    "curso_id": cursos_por_chave[chave],
                    "alunos_ativos": registro["alunos_ativos"],
                    "alunos_evadidos": registro["alunos_evadidos"],
                }
                for chave, registro in dados_atuais.items()
            ]
            conexao.execute(
                text(
                    "UPDATE curso SET alunos_ativos = :alunos_ativos, "
                    "alunos_evadidos = :alunos_evadidos WHERE id = :curso_id"
                ),
                cursos_atualizados,
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
    except SQLAlchemyError as error:
        raise RuntimeError(
            "Não foi possível ler ou sincronizar a tabela cursos. "
            "Confirme a conexão e a estrutura da tabela no Supabase."
        ) from error

    print(f"ETL concluído: {len(registros)} registro(s) sincronizado(s).")
    return len(registros)


if __name__ == "__main__":
    executar_etl()
