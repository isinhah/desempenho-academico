import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Configuração do ambiente e conexão
# carrega as variáveis de ambiente do .env
load_dotenv()

# cria o motor de conexão do SQLAlchemy a partir da URL do banco de dados
engine = create_engine(os.getenv("DATABASE_URL"))

# 2. Leitura do arquivo de dados
df = pd.read_csv("cursos.csv")

# 3. Função para cálculo da regra de negócio
def calcular_pct_evasao(row):
    if row["alunos_ativos"] == 0:
        return 0
    return round((row["alunos_evadidos"] / row["alunos_ativos"]) * 100, 2)

# 4. Aplicação do cálculo no dataframe
df["pct_evasao"] = df.apply(calcular_pct_evasao, axis=1)
print(df)

# 5. Persistência no banco de dados
# O 'engine.begin()' abre uma transação que faz COMMIT automático ao terminar
# (ou ROLLBACK se ocorrer algum erro)
with engine.begin() as conexao:
    # Percorre cada linha do DataFrame
    for _, linha in df.iterrows():

        # A) ESCOLA: Procura o ID da escola pelo nome
        escola_id = conexao.execute(
            text("SELECT id FROM escola WHERE nome = :nome"),
            {"nome": linha["escola"]},
        ).scalar()

        # Se a escola não existir no banco, faz a inserção e recupera o ID gerado
        if escola_id is None:
            escola_id = conexao.execute(
                text("INSERT INTO escola (nome) VALUES (:nome) RETURNING id"),
                {"nome": linha["escola"]},
            ).scalar()

        # B) CURSO: Procura o ID do curso vinculado à escola
        curso_id = conexao.execute(
            text("SELECT id FROM curso WHERE escola_id = :escola_id AND nome = :nome"),
            {"escola_id": escola_id, "nome": linha["curso"]},
        ).scalar()

        # Se o curso não existir no banco, insere o curso associado à escola
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

        # C) HISTÓRICO: Regista a métrica/indicador calculado na tabela de histórico
        conexao.execute(
            text(
                "INSERT INTO historico_indicador "
                "(curso_id, mes_referencia, pct_evasao) "
                "VALUES (:curso_id, CURRENT_DATE, :pct_evasao)"
            ),
            {"curso_id": curso_id, "pct_evasao": linha["pct_evasao"]},
        )

print("Dados inseridos no banco de dados com sucesso!")
