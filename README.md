# Ranking de desempenho de cursos

Projeto educacional para análise de desempenho de cursos de uma faculdade. A aplicação apresenta um ranking de cursos, permite filtrar por escola e classe, e detalha score, evasão e evolução histórica de cada curso.

## Objetivo

Uma aplicaçaõ com uma fonte de dados no Supabase, um processo de ETL para validar e consolidar os indicadores, uma API FastAPI somente de leitura e um dashboard React para exploração dos resultados.

## Tecnologias

- **Frontend:** React, Vite, Tailwind CSS e Recharts.
- **API:** Python 3.12, FastAPI, SQLAlchemy, Psycopg e Pydantic.
- **Banco de dados:** PostgreSQL hospedado no Supabase.
- **Infraestrutura local:** Docker e Docker Compose.

## Arquitetura

```mermaid
flowchart LR
    frontend[Frontend<br/>React + Vite] --> api[API<br/>FastAPI]
    api --> supabase[(Supabase<br/>PostgreSQL)]
    fonte["cursos<br/>fonte oficial"] --> etl["ETL<br/>sincronizar_dados_cursos"]
    etl --> analiticas["escola, curso e<br/>historico_indicador"]
    analiticas --> api
    admin["Administrador"] --> endpoint["POST /administracao/<br/>sincronizar-dados"]
    endpoint --> etl
```

## Fluxo dos dados

1. A tabela `cursos` do Supabase é a fonte oficial e contém os dados brutos por curso e mês.
2. O ETL valida os registros, calcula o percentual de evasão e atualiza as tabelas analíticas `escola`, `curso` e `historico_indicador`.
3. A API consulta somente as tabelas analíticas para montar o ranking e o histórico.
4. O frontend consome a API para exibir filtros, ranking, score, indicadores do período mais recente e gráfico de evasão.
5. Uma pessoa administradora pode disparar o ETL pela rota protegida, usando um token mantido apenas no ambiente do backend.

## Modelo de dados

| Tabela | Papel |
| --- | --- |
| `cursos` | Fonte oficial no Supabase: escola, curso, alunos ativos, alunos evadidos e mês de referência. |
| `escola` | Cadastro analítico das escolas. |
| `curso` | Estado mais recente de alunos ativos e evadidos por curso. |
| `historico_indicador` | Percentual de evasão por curso e mês. |

### Cálculo de evasão

```text
percentual de evasão = (alunos evadidos / alunos ativos) × 100
```

O ETL rejeita registros sem escola, curso ou mês de referência, bem como números negativos e situações em que alunos evadidos sejam maiores que alunos ativos.

### Score e classes

O score consolidado vai de 0 a 100 e combina uma dimensão financeira com peso de 55% e uma dimensão acadêmica com peso de 45%. A dimensão acadêmica é reduzida conforme a evasão aumenta.

| Classe | Score |
| --- | --- |
| A | Maior ou igual a 80 |
| B | De 60 até 79,99 |
| D | Menor que 60 |

## Endpoints principais

### API — `http://localhost:8000`

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/` | Confirma que a API está no ar. |
| `GET` | `/health/database` | Verifica a conexão da API com o Supabase. |
| `GET` | `/escolas` | Lista escolas disponíveis no filtro. |
| `GET` | `/cursos` | Retorna o ranking, ordenado por score. |
| `GET` | `/cursos?escola_id={id}` | Retorna o ranking filtrado por escola. |
| `GET` | `/cursos/{id}` | Retorna os indicadores atuais de um curso. |
| `GET` | `/cursos/{id}/historico` | Retorna a evolução mensal da evasão. |
| `POST` | `/administracao/sincronizar-dados` | Executa o ETL; exige o cabeçalho `X-Admin-Token`. |

A documentação interativa está disponível em [http://localhost:8000/docs](http://localhost:8000/docs).

## Configuração

### Pré-requisitos

- Docker com Docker Compose.
- Node.js 20+ e npm, para executar o frontend localmente.
- Um projeto Supabase com acesso ao banco PostgreSQL.

### Variáveis de ambiente

Crie o arquivo de ambiente do backend a partir do exemplo:

```bash
cp backend/.env.example backend/.env
```

Gere um token aleatório:

```bash
openssl rand -hex 32
```

Edite `backend/.env` com a URL do **Session pooler** obtida no painel do Supabase e use o valor gerado em `ADMIN_API_TOKEN`:

```env
DATABASE_URL=postgresql+psycopg://postgres.PROJECT_REF:SUA_SENHA@HOST_DO_SESSION_POOLER:5432/postgres?sslmode=require
ADMIN_API_TOKEN=um-token-longo-e-aleatorio
```

> Nunca envie o arquivo `backend/.env` ou o token para o Git.

### Integridade do banco

Antes da primeira sincronização, copie o **conteúdo** de [`backend/migrations/001_integridade_dados_analiticos.sql`](backend/migrations/001_integridade_dados_analiticos.sql) e execute-o uma vez no SQL Editor do Supabase. A migration cria restrições que evitam registros duplicados.

## Comandos

### Subir a API

```bash
docker compose up --build -d
```

### Acompanhar os logs

```bash
docker compose logs -f api
```

### Executar o frontend

```bash
cd frontend
npm install
npm run dev
```

Abra o frontend em [http://localhost:5173](http://localhost:5173).

### Sincronizar dados e calcular evasão

Após cadastrar ou atualizar registros na tabela `cursos` do Supabase, execute o ETL pela rota administrativa:

```bash
curl -X POST http://localhost:8000/administracao/sincronizar-dados \
  -H "X-Admin-Token: SEU_TOKEN"
```

Exemplo de resposta:

```json
{
  "mensagem": "Dados sincronizados com sucesso.",
  "registros_sincronizados": 864
}
```

Como alternativa para desenvolvimento local, execute o módulo dentro do container:

```bash
docker compose exec api python -m app.domain.sincronizar_dados_cursos
```

### Validar o frontend

```bash
cd frontend
npm run lint
npm run build
```

### Parar a API

```bash
docker compose down
```

## Interfaces

| Serviço | Endereço |
| --- | --- |
| Frontend | [http://localhost:5173](http://localhost:5173) |
| API | [http://localhost:8000](http://localhost:8000) |
| Swagger | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Supabase | Painel do projeto configurado em `DATABASE_URL` |

## Persistência

Os dados são persistidos no PostgreSQL do Supabase, e não em um volume Docker local.

A tabela `cursos` continua sendo a origem dos dados; execute a sincronização sempre que os dados dela forem inseridos ou atualizados.
