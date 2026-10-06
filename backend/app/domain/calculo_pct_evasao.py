from calendar import monthrange
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.database import engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "cursos.csv"

# calcula a evasão percentual de uma linha do csv
def calcular_pct_evasao(row):
    if row["alunos_ativos"] == 0:
        return 0
    return round((row["alunos_evadidos"] / row["alunos_ativos"]) * 100, 2)


def subtrair_meses(data: date, meses: int) -> date:
    """Retorna uma data no mês anterior, preservando o dia quando possível."""
    indice_mes = data.year * 12 + data.month - 1 - meses
    ano, mes_zero_indexado = divmod(indice_mes, 12)
    mes = mes_zero_indexado + 1
    return date(ano, mes, min(data.day, monthrange(ano, mes)[1]))


def gerar_historico_ficticio(pct_evasao: float) -> list[tuple[date, float]]:
    """Gera três meses para demonstrar a evolução do indicador no dashboard."""
    hoje = date.today()
    variacoes = [(2, 1.2), (1, 0.6), (0, 0)]
    return [
        (subtrair_meses(hoje, meses), round(min(100, max(0, pct_evasao + variacao)), 2))
        for meses, variacao in variacoes
    ]


def inserir_historico_ficticio(conexao, curso_id: int, pct_evasao: float) -> None:
    """Insere os meses de demonstração que ainda não existirem para o curso."""
    for mes_referencia, valor_evasao in gerar_historico_ficticio(pct_evasao):
        conexao.execute(
            text(
                "INSERT INTO historico_indicador "
                "(curso_id, mes_referencia, pct_evasao) "
                "SELECT :curso_id, :mes_referencia, :pct_evasao "
                "WHERE NOT EXISTS ("
                "SELECT 1 FROM historico_indicador "
                "WHERE curso_id = :curso_id AND mes_referencia = :mes_referencia"
                ")"
            ),
            {
                "curso_id": curso_id,
                "mes_referencia": mes_referencia,
                "pct_evasao": valor_evasao,
            },
        )

# lê o csv da raiz, calcula a evasão e salva seus indicadores
def executar_etl() -> None:
    df = pd.read_csv(CSV_PATH)
    df["pct_evasao"] = df.apply(calcular_pct_evasao, axis=1)
    print(df)

    # engine.begin() faz commit ao concluir ou rollback em caso de erro.
    with engine.begin() as conexao:
        for _, linha in df.iterrows():
            escola_id = conexao.execute(
                text("SELECT id FROM escola WHERE nome = :nome"),
                {"nome": linha["escola"]},
            ).scalar()

            if escola_id is None:
                escola_id = conexao.execute(
                    text("INSERT INTO escola (nome) VALUES (:nome) RETURNING id"),
                    {"nome": linha["escola"]},
                ).scalar()

            curso_id = conexao.execute(
                text("SELECT id FROM curso WHERE escola_id = :escola_id AND nome = :nome"),
                {"escola_id": escola_id, "nome": linha["curso"]},
            ).scalar()

            if curso_id is None:
                curso_id = conexao.execute(
                    text(
                        "INSERT INTO curso (escola_id, nome, alunos_ativos, alunos_evadidos) "
                        "VALUES (:escola_id, :nome, :ativos, :evadidos) RETURNING id"
                    ),
                    {
                        "escola_id": escola_id,
                        "nome": linha["curso"],
                        "ativos": linha["alunos_ativos"],
                        "evadidos": linha["alunos_evadidos"],
                    },
                ).scalar()

        cursos = conexao.execute(
            text("SELECT id, alunos_ativos, alunos_evadidos FROM curso")
        ).mappings()
        for curso in cursos:
            pct_evasao = calcular_pct_evasao(curso)
            inserir_historico_ficticio(conexao, curso["id"], pct_evasao)

    print("Dados inseridos no banco de dados com sucesso!")


if __name__ == "__main__":
    executar_etl()
