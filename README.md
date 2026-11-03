# Desempenho acadêmico e evasão dos cursos

Projeto educacional para análise de desempenho acadêmico e evasão de cursos de uma faculdade. A aplicação apresenta um ranking acadêmico, permite filtrar por escola e classe, e detalha score, evasão e evolução histórica de cada curso.

## Objetivo

Uma aplicaçaõ com uma fonte de dados no Supabase, um processo de ETL para validar e consolidar os indicadores, uma API FastAPI somente de leitura e um dashboard React para exploração dos resultados.

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
    fonte["cursos<br/>fonte oficial"] --> etl["ETL<br/>sincronizar_dados_cursos"]
    etl --> analiticas["escola, curso e<br/>historico_indicador"]
    analiticas --> api
    admin["Administrador"] --> endpoint["POST /administracao/<br/>sincronizar-dados"]
    endpoint --> etl
    scheduler[Scheduler] -->|report.generate| rabbit[RabbitMQ]
    rabbit -->|report.generate| worker[Report worker]
    worker --> analiticas
    worker -->|report.send| rabbit
    rabbit -->|report.send| notifier[Notifier]
    notifier --> mailpit[Mailpit]
```

## Fluxo dos dados

1. A tabela `cursos` do Supabase é a fonte oficial e contém os dados brutos por curso e mês.
2. O ETL valida os registros, calcula o percentual de evasão, atualiza as tabelas analíticas e grava um resumo acadêmico determinístico por curso.
3. A API consulta somente as tabelas analíticas para montar o ranking e o histórico.
4. O frontend consome a API para exibir filtros, ranking, score, indicadores do período mais recente e gráfico de evasão.
5. Uma pessoa administradora pode disparar o ETL pela rota protegida, usando um token mantido apenas no ambiente do backend.
6. No primeiro dia de cada mês, o scheduler publica uma solicitação de relatório para o último mês concluído.
7. O report worker identifica os perfis ativos e monta um resumo institucional para cada decano ou um resumo dos cursos vinculados para cada coordenador.
8. O notifier envia cada e-mail ao endereço cadastrado no Supabase Auth; eles podem ser visualizados no Mailpit.

## Modelo de dados

| Tabela | Papel |
| --- | --- |
| `cursos` | Fonte oficial no Supabase: escola, curso, alunos ativos, alunos evadidos e mês de referência. |
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
SUPABASE_URL=https://SEU_PROJECT_REF.supabase.co
RABBITMQ_URL=amqp://app:app@rabbitmq:5672/%2F
EMAIL_FROM=relatorios@faculdade.br
SMTP_HOST=mailpit
SMTP_PORT=1025
REPORT_TIMEZONE=America/Sao_Paulo
REPORT_SCHEDULE_DAY=1
REPORT_SCHEDULE_HOUR=8
REPORT_RUN_ON_STARTUP=false
```

> Nunca envie o arquivo `backend/.env` ou o token para o Git.

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

Os dados são persistidos no PostgreSQL do Supabase, e não em um volume Docker local.

A tabela `cursos` continua sendo a origem dos dados; execute a sincronização sempre que os dados dela forem inseridos ou atualizados.
