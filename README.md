# Desempenho acadêmico e evasão dos cursos

Projeto educacional para análise de desempenho acadêmico e evasão de cursos de uma faculdade. A aplicação apresenta um ranking acadêmico, permite filtrar por escola e classe, e detalha score, evasão e evolução histórica de cada curso.

## Objetivo

Uma aplicação com uma fonte de dados no Supabase, um processo de ETL para validar e consolidar os indicadores, uma API FastAPI somente de leitura e um dashboard React para exploração dos resultados.

## Tecnologias

- **Frontend:** React, Vite, Tailwind CSS e Recharts.
- **API:** Python 3.12, FastAPI, SQLAlchemy, Psycopg e Pydantic.
- **Banco de dados:** PostgreSQL hospedado no Supabase.
- **Processamento assíncrono:** RabbitMQ.
- **E-mail de desenvolvimento:** Mailpit.
- **Infraestrutura local:** Docker e Docker Compose.

## Arquitetura

```mermaid
flowchart LR
    frontend[Frontend<br/>React + Vite] --> api[API<br/>FastAPI]
    api --> supabase[(Supabase<br/>PostgreSQL)]
    storage["Supabase Storage<br/>CSVs mensais"] --> importacao["Importação<br/>validar e registrar"]
    importacao --> bruto["curso_indicador_bruto"]
    bruto --> etl["ETL<br/>sincronizar_dados_cursos"]
    etl --> analiticas["escola, curso e<br/>historico_indicador"]
    analiticas --> api
    admin["Administrador"] --> endpoint["POST /administracao/importacoes/processar"]
    endpoint --> importacao
    scheduler[Scheduler] -->|report.generate| rabbit[RabbitMQ]
    rabbit -->|report.generate| worker[Report worker]
    worker --> analiticas
    worker -->|report.send| rabbit
    rabbit -->|report.send| notifier[Notifier]
    notifier --> mailpit[Mailpit]
```

## Fluxo dos dados

1. Um CSV por mês é enviado ao bucket privado `importacoes-cursos` do Supabase Storage.
2. O endpoint administrativo baixa, valida e registra as 72 linhas do arquivo em `curso_indicador_bruto`, com rastreabilidade em `importacao_arquivo`.
3. O ETL processa somente a importação registrada, calcula o percentual de evasão, atualiza as tabelas analíticas e grava um resumo acadêmico determinístico por curso.
4. A API consulta somente as tabelas analíticas para montar o ranking e o histórico.
5. O frontend consome a API para exibir filtros, ranking, score, indicadores do período mais recente e gráfico de evasão.
6. Uma pessoa administradora pode processar um CSV pela rota protegida, usando um token mantido apenas no ambiente do backend.
7. No primeiro dia de cada mês, o scheduler publica uma solicitação de relatório para o último mês concluído.
8. O report worker identifica os perfis ativos e monta um resumo institucional para cada decano ou um resumo dos cursos vinculados para cada coordenador.
9. O notifier envia cada e-mail ao endereço cadastrado no Supabase Auth; eles podem ser visualizados no Mailpit.

## Modelo de dados

| Tabela | Papel |
| --- | --- |
| `importacao_arquivo` | Rastreia cada CSV enviado ao Storage, seu mês e o resultado do processamento. |
| `curso_indicador_bruto` | Fonte bruta oficial por curso e mês, originada nos CSVs mensais. |
| `escola` | Cadastro analítico das escolas. |
| `curso` | Estado mais recente de alunos, resumo acadêmico e data de referência por curso. |
| `historico_indicador` | Percentual de evasão por curso e mês. |
| `perfil_usuario` | Papel e situação de acesso de cada usuário autenticado. |
| `usuario_curso` | Cursos que cada coordenador pode consultar. |

### Cálculo de evasão

```text
percentual de evasão = (alunos evadidos / alunos ativos) × 100
```

O ETL rejeita registros sem escola, curso ou mês de referência, bem como números negativos e situações em que alunos evadidos sejam maiores que alunos ativos.

### Resumo automático do curso

Ao final de cada sincronização, o ETL analisa o histórico de evasão e grava um parágrafo no curso, por exemplo: “A evasão sobe há 6 meses, de 26,00% para 29,75%. O score atual é 63,33, na Classe B.” A API retorna esse texto pronto na tela de detalhe; ele não é recalculado a cada visita.

### Score e classes

No estado atual do projeto, a evasão é o único indicador acadêmico alimentado por dados. O score de 0 a 100 é uma regra didática: combina uma base financeira fixa de 55% com uma dimensão acadêmica de 45%, reduzida conforme a evasão aumenta. As dimensões de mercado, finanças e qualidade ainda não são exibidas como indicadores, pois não possuem dados de origem.

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
| `GET` | `/autenticacao/me` | Retorna o perfil e os cursos permitidos ao usuário autenticado. |
| `GET` | `/escolas` | Lista escolas disponíveis no filtro. |
| `GET` | `/cursos` | Retorna o ranking, ordenado por score. |
| `GET` | `/cursos?escola_id={id}` | Retorna o ranking filtrado por escola. |
| `GET` | `/cursos/{id}` | Retorna os indicadores atuais de um curso. |
| `GET` | `/cursos/{id}/historico` | Retorna a evolução mensal da evasão. |
| `POST` | `/administracao/importacoes/processar` | Valida e processa um CSV mensal do Storage; exige `X-Admin-Token`. |

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
SUPABASE_URL=https://SEU_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=SUA_CHAVE_SECRETA_DO_SUPABASE
SUPABASE_STORAGE_BUCKET=importacoes-cursos
RABBITMQ_URL=amqp://app:app@rabbitmq:5672/%2F
EMAIL_FROM=relatorios@faculdade.br
SMTP_HOST=mailpit
SMTP_PORT=1025
REPORT_TIMEZONE=America/Sao_Paulo
REPORT_SCHEDULE_DAY=1
REPORT_SCHEDULE_HOUR=8
REPORT_RUN_ON_STARTUP=false
```

> A chave secreta/service_role é usada somente pelo backend para acessar o bucket privado. Nunca envie `backend/.env`, o token administrativo ou essa chave ao Git; ela nunca deve ser usada no frontend.

### Autenticação e autorização

Execute também o conteúdo de [`backend/migrations/002_perfis_e_acessos.sql`](backend/migrations/002_perfis_e_acessos.sql) no SQL Editor do Supabase. Em seguida, crie os usuários em **Authentication → Users** no painel do Supabase e associe cada um a um perfil em `perfil_usuario`.

- `DECANO`: consulta ranking, escolas e todos os cursos.
- `COORDENADOR_CURSO`: consulta somente os cursos presentes em `usuario_curso`.

No frontend, crie `frontend/.env` a partir do exemplo e informe a URL do projeto e a chave `anon`/`publishable` em **Project Settings → API**:

```bash
cp frontend/.env.example frontend/.env
```

> A chave `service_role` nunca deve ser usada no frontend.

### Integridade do banco

Antes da primeira sincronização, copie o **conteúdo** das migrations e execute-as uma vez no SQL Editor do Supabase, nesta ordem:

1. [`backend/migrations/001_integridade_dados_analiticos.sql`](backend/migrations/001_integridade_dados_analiticos.sql): restrições contra duplicidade.
2. [`backend/migrations/002_perfis_e_acessos.sql`](backend/migrations/002_perfis_e_acessos.sql): perfis de acesso e vínculos de coordenadores.
3. [`backend/migrations/003_resumo_academico_curso.sql`](backend/migrations/003_resumo_academico_curso.sql): campos do resumo automático.
4. [`backend/migrations/004_importacoes_csv.sql`](backend/migrations/004_importacoes_csv.sql): controle de CSVs mensais e dados brutos importados.

## Comandos

### Subir os serviços

```bash
docker compose up --build -d
```

### Acompanhar os logs

```bash
docker compose logs -f api
docker compose logs -f scheduler report-worker notifier
```

### Executar o frontend

```bash
cd frontend
npm install
npm run dev
```

Abra o frontend em [http://localhost:5173](http://localhost:5173).

### Processar um CSV mensal do Supabase Storage

Crie no painel do Supabase um bucket **privado** chamado `importacoes-cursos`. Envie para ele um arquivo no formato `cursos_YYYY-MM.csv`, com os cabeçalhos abaixo e exatamente 72 linhas de dados:

```text
escola,curso,alunos_ativos,alunos_evadidos,mes_referencia
```

Depois, processe somente o arquivo enviado. O `caminho_storage` é o caminho dentro do bucket; neste exemplo, o arquivo está na raiz:

```bash
curl -X POST http://localhost:8000/administracao/importacoes/processar \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: SEU_TOKEN" \
  -d '{"caminho_storage":"cursos_2026-10.csv"}'
```

Exemplo de resposta:

```json
{
  "importacao_id": 1,
  "caminho_storage": "cursos_2026-10.csv",
  "mes_referencia": "2026-10-01",
  "linhas_lidas": 72,
  "linhas_importadas": 72,
  "registros_sincronizados": 72,
  "status": "CONCLUIDA"
}
```

O mesmo caminho não pode ser processado duas vezes; para uma correção, envie o CSV para um novo caminho, por exemplo `correcoes/cursos_2026-10_v2.csv`. O nome final do arquivo continua precisando seguir `cursos_YYYY-MM.csv`.

### Preparar CSVs mensais locais

Para validar a base histórica sintética e separá-la em um arquivo por competência, execute:

```bash
python3 backend/scripts/separar_csvs_mensais.py
```

O script lê `backend/data/cursos_historico_mensal.csv`, exige 864 linhas (72 cursos em 12 meses) e gera os arquivos em `backend/data/entrada/`, como `cursos_2026-10.csv`. Ele não envia dados ao Supabase.

Para usar outro arquivo de origem, informe o caminho explicitamente:

```bash
python3 backend/scripts/separar_csvs_mensais.py \
  --arquivo backend/data/cursos_historico_2025-11_a_2026-10.csv
```

Por segurança, o script não substitui CSVs mensais já existentes. Use `--sobrescrever` apenas quando quiser recriá-los.

### Relatório mensal automático

O scheduler executa no dia e hora definidos por `REPORT_SCHEDULE_DAY` e `REPORT_SCHEDULE_HOUR`, usando o fuso de `REPORT_TIMEZONE`. Ele sempre gera o relatório do mês anterior ao mês da execução.

Para testar localmente sem esperar o próximo agendamento, altere temporariamente no `backend/.env`:

```env
REPORT_RUN_ON_STARTUP=true
```

Em seguida, recrie os serviços:

```bash
docker compose up --build -d
```

O report worker usa os perfis ativos vinculados ao Supabase Auth como destinatários:

- Cada `DECANO` recebe um resumo institucional: cursos analisados, score médio, distribuição por classe, cinco melhorias e cinco cursos em atenção.
- Cada `COORDENADOR_CURSO` recebe um único e-mail com o score, a classe, a evasão e as variações mensais de todos os seus cursos vinculados.

O endereço de envio vem de `EMAIL_FROM`; o endereço de destino é o e-mail do usuário no Supabase Auth. Coordenadores sem curso vinculado não recebem e-mail e geram um aviso nos logs do worker.

Depois do teste, retorne `REPORT_RUN_ON_STARTUP` para `false` para não publicar o relatório novamente em cada reinicialização do scheduler.

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
| RabbitMQ Management | [http://localhost:15672](http://localhost:15672) (`app` / `app`) |
| Mailpit | [http://localhost:8025](http://localhost:8025) |

## Persistência

Os dados analíticos e o controle das importações são persistidos no PostgreSQL do Supabase, e os CSVs de entrada ficam no Supabase Storage; não há volume Docker local para esses dados.
