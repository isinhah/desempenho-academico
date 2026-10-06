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

            conexao.execute(
                text(
                    "INSERT INTO historico_indicador "
                    "(curso_id, mes_referencia, pct_evasao) "
                    "VALUES (:curso_id, CURRENT_DATE, :pct_evasao)"
                ),
                {"curso_id": curso_id, "pct_evasao": linha["pct_evasao"]},
            )

    print("Dados inseridos no banco de dados com sucesso!")


if __name__ == "__main__":
    executar_etl()
