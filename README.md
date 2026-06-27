# QueryPilot: Safe Text-to-SQL Analytics Agent

QueryPilot is a personal Data & AI Engineering project for building a safe Text-to-SQL analytics backend step by step.

The project uses synthetic e-commerce data and a demo query provider. It does not require an external model or API key yet.

## Why I Am Building It

Text-to-SQL is useful, but it can be risky if generated queries run without checks. This project focuses on the backend workflow around analytics questions:

1. inspect the database schema
2. generate or select a SQL query
3. validate the SQL before execution
4. block dangerous SQL
5. execute only safe read-only queries
6. return structured results
7. log what happened
8. collect feedback
9. evaluate the system with demo questions

The goal is to keep the system easy to inspect, test, and explain.

## What It Does Now

The current backend includes:

- FastAPI routes for health, chat, SQL validation, analytics, query history, feedback, evaluation, schema context, and prompt context.
- SQLAlchemy models for the synthetic e-commerce database.
- A demo query provider that maps known business questions to safe SQL templates.
- A provider interface and LLM skeleton for future work, with demo mode still the default.
- A prompt context builder for future LLM providers.
- SQL validation before query execution.
- Query history, feedback, and evaluation tests.
- Docker Compose and GitHub Actions for local running and CI.

## Architecture

```text
backend/
  app/
    main.py
    api/
      routes/
        analytics.py
        chat.py
        evaluation.py
        feedback.py
        health.py
        prompt.py
        queries.py
        schema_context.py
    core/
      config.py
      database.py
    demo/
      evaluation_questions.py
      seed_data.py
    models/
      database_models.py
      schemas.py
    prompting/
      builder.py
    providers/
      base.py
      demo_provider.py
      factory.py
      llm_provider.py
    schema_context/
      catalog.py
      models.py
      service.py
    services/
      analytics_service.py
      chat_service.py
      evaluation_service.py
      explanation_service.py
      feedback_service.py
      logging_service.py
      query_execution_service.py
      sql_validation_service.py
  tests/
    test_analytics_routes.py
    test_chat.py
    test_database_models.py
    test_evaluation.py
    test_health.py
    test_prompt_context.py
    test_provider.py
    test_query_logs_feedback.py
    test_schema_context.py
    test_sql_validation.py
docs/
  api_examples.md
  database_schema.md
```

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Docker Compose
- pytest

## How To Run

```bash
docker compose up --build
```

Then check the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Seed The Demo Database

After the containers are running, seed the synthetic e-commerce data:

```bash
docker compose exec backend python -m app.demo.seed_data
```

The seed data is small on purpose. It supports analytics endpoint development and manual demos without using private data.

## Testing

Run backend tests locally from the repository root:

```bash
cd backend
python -m pytest
```

GitHub Actions also runs the backend test workflow on pull requests.

## Provider Interface

QueryPilot uses the demo provider by default. It maps known business questions to SQL templates so the project can run locally without external services.

The provider interface is there for future LLM support. Any generated SQL still needs to pass validation before execution.

The default provider is configured with:

```text
QUERY_PROVIDER=demo
```

## Schema Context

The schema context layer describes the demo database tables, columns, relationships, and business meaning.

Future providers can use this context to generate better SQL, while the validation layer still checks every query before execution.

## Prompt Context

Before adding a real LLM provider, I added a small prompt context builder. It prepares the information a provider will need: the question, the database schema, safety rules, and the expected response format. The demo provider still stays the default path.

## Evaluation

The project includes a small evaluation suite for the demo agent.

The cases include normal business questions, unsupported questions, and unsafe questions. The suite checks whether questions map to the expected category, unsupported questions are handled cleanly, and unsafe questions are blocked.

## Example Questions

- What are the top 5 products by revenue?
- What is the monthly revenue trend?
- Which customer segment generates the most revenue?
- What is the refund rate by product category?

## Current API

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
GET  /schema
GET  /schema/tables/{table_name}
GET  /schema/compact
GET  /analytics/top-products
GET  /analytics/monthly-revenue
GET  /analytics/refund-rate
GET  /analytics/customer-segments
```

## SQL Safety Rules

The SQL safety layer allows only read-only analytics queries.

Allowed:

- `SELECT`
- `WITH`

Blocked:

- `DROP`
- `DELETE`
- `UPDATE`
- `INSERT`
- `ALTER`
- `TRUNCATE`
- `CREATE`
- `GRANT`
- `REVOKE`
- `COPY`
- `EXEC`
- `MERGE`
- `CALL`

It also blocks multiple statements, SQL comments, suspicious semicolons, and broad `SELECT *` queries without a `LIMIT`.

## Roadmap

Next milestone:

- add a real provider behind the existing provider interface
- keep the demo provider as the default path
- keep SQL validation mandatory before execution

Later:

- keep the basic demo runnable without an API key
- add a small UI or docs demo if the backend is stable
