# QueryPilot: Safe Text-to-SQL Analytics Agent

QueryPilot is a FastAPI backend that answers analytics questions with SQL while keeping validation between query generation and execution.

The project runs against synthetic e-commerce data. Its deterministic demo provider is the default, so the complete local flow works without an external model or API key. An optional NVIDIA-compatible provider is available for testing LLM-generated SQL through the same validation path.

## Why safe Text-to-SQL matters

Text-to-SQL makes data easier to explore, but generated SQL should be treated as untrusted input. A useful system needs more than query generation: it needs schema context, validation, controlled execution, logging, feedback, and repeatable evaluation.

QueryPilot follows this flow:

1. receive an analytics question
2. select or generate a SQL candidate through a provider
3. validate the SQL as read-only
4. block unsafe or unsupported requests
5. execute approved SQL against PostgreSQL
6. return structured results and record the interaction

## Current features

- FastAPI endpoints for chat, SQL validation, analytics, query history, feedback, provider evaluation, schema context, and prompt context
- Synthetic PostgreSQL e-commerce schema and seed data
- Deterministic demo provider with no API key required
- Optional NVIDIA-compatible LLM provider behind the same provider interface
- Read-only SQL validation before execution
- Query logging and user feedback storage
- Evaluation cases for supported, unsupported, and unsafe questions
- Provider comparison with per-provider results and summaries
- Docker Compose for local services and GitHub Actions for backend tests

## Try it locally

Requirements: Docker, Docker Compose, and `curl`.

1. Start PostgreSQL and the backend:

```bash
docker compose up --build -d
```

2. Seed the synthetic data:

```bash
docker compose exec backend python -m app.demo.seed_data
```

3. Ask a demo question:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the top 5 products by revenue?"}'
```

4. Run the evaluation suite with the default demo provider:

```bash
curl -X POST http://localhost:8000/evaluation/run
```

5. Compare the demo and LLM providers:

```bash
curl -X POST http://localhost:8000/evaluation/compare
```

If the LLM provider is not configured, the comparison reports `not_configured` for that provider instead of failing.

To stop the services:

```bash
docker compose down
```

## Guides

- [Local demo guide](docs/demo.md)
- [Presentation notes](docs/presentation_notes.md)
- [API examples](docs/api_examples.md)

## Run the tests

From the repository root, install the backend requirements in your Python environment and run pytest:

```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest
```

GitHub Actions runs the backend test suite on pull requests.

## Architecture

The API routes stay thin. Providers produce query candidates, services handle validation and execution, and Pydantic models define the API contracts.

The backend uses Python 3.12, FastAPI, SQLAlchemy, Pydantic, PostgreSQL, and pytest.

```text
backend/
  app/
    api/routes/          FastAPI endpoints
    core/                configuration and database setup
    demo/                seed data and evaluation cases
    models/              API and database models
    prompting/           prompt context builder
    providers/           demo and LLM provider implementations
    schema_context/      schema metadata and compact context
    services/            validation, execution, logging, and evaluation
    main.py              application setup
  tests/                 backend test suite
docs/
  api_examples.md
  database_schema.md
  demo.md
  presentation_notes.md
```

## Provider design

### Demo provider

The demo provider is the default path:

```text
QUERY_PROVIDER=demo
```

It maps supported business questions to known SQL templates. This keeps the project deterministic and runnable without external services.

### Optional NVIDIA-compatible provider

The LLM provider uses an NVIDIA-compatible chat-completions endpoint when all required settings are present:

```text
QUERY_PROVIDER=llm
LLM_PROVIDER=nvidia
LLM_MODEL=<model-name>
LLM_API_BASE_URL=<nvidia-compatible-chat-completions-base-url>
LLM_API_KEY=<your-api-key>
```

The provider prepares a prompt, parses the response into a SQL candidate, and returns safe failure results for missing configuration or invalid responses. Generated SQL never bypasses the existing validation layer.

### Schema context and prompt context

Schema context describes the demo tables, columns, relationships, and business meaning. Prompt context combines the question, compact schema context, safety rules, and expected response format for the LLM provider.

Both contexts can also be inspected through the API, which makes provider inputs easier to debug and test.

## Provider evaluation

The evaluation suite uses the same cases across providers. Each result records the expected and actual category, expected and actual safety status, provider, parseability, SQL generation, SQL validation, pass status, and reason.

- `POST /evaluation/run` uses the demo provider by default and accepts an optional provider selection.
- `POST /evaluation/compare` runs the same cases for the demo and LLM providers and groups results and summaries by provider.

The suite includes normal analytics questions, unsupported topics, and unsafe requests. Tests use mocks for LLM responses and do not call real external APIs.

## SQL safety rules

The validator allows read-only queries beginning with `SELECT` or `WITH`. It blocks write and administrative statements such as `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, and `CREATE`.

It also rejects multiple statements, SQL comments, suspicious semicolons, and unrestricted `SELECT *` queries without a `LIMIT`.

## API overview

```text
GET  /health
POST /chat
POST /validate-sql
POST /prompt/context
GET  /queries/logs
GET  /queries/logs/{query_log_id}
POST /feedback
GET  /feedback/query/{query_log_id}
GET  /evaluation/cases
POST /evaluation/run
POST /evaluation/compare
GET  /schema
GET  /schema/tables/{table_name}
GET  /schema/compact
GET  /analytics/top-products
GET  /analytics/monthly-revenue
GET  /analytics/refund-rate
GET  /analytics/customer-segments
```

## Current limitations

- The demo provider is deterministic and supports a limited set of known analytics questions.
- The NVIDIA-compatible provider requires user configuration and a compatible external model endpoint.
- Real LLM behavior should be checked manually with user-provided credentials; automated tests use mocks only.
- Every generated SQL candidate is validated before execution, but the current validator focuses on application-level read-only rules.
- The project currently uses synthetic e-commerce data and a single PostgreSQL schema.

## Possible improvements

- expand evaluation cases and supported analytics questions
- add database-level read-only credentials, query timeouts, and row limits
- measure configured LLM accuracy, latency, and failure modes in a controlled environment
- extend schema coverage and support additional SQL dialects
