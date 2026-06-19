# QueryPilot: Safe Text-to-SQL Analytics Agent

This is a personal Data & AI Engineering project where I am building a safe Text-to-SQL analytics agent step by step.

The goal is not only to generate SQL. I also want to validate it, execute it safely, keep query history, collect feedback, and evaluate the system with demo questions.

For now, the project uses synthetic e-commerce data and a simple demo question mapping. There is no external model required yet.

## Why I Am Building It

Text-to-SQL can be useful, but it can also be risky if queries are generated and executed without checks. This project focuses on the backend workflow around analytics questions:

1. understand the user question
2. inspect the database schema
3. generate or select a SQL query
4. validate the SQL before execution
5. block dangerous SQL
6. execute only safe read-only queries
7. return structured results
8. explain the answer
9. log the question, SQL, result, and errors
10. collect feedback
11. evaluate the agent with test questions

A Text-to-SQL agent should not be a black box. I want to track what was asked, what SQL was generated, whether it was safe, and whether the answer was useful.

## What It Does Now

Milestone 7 adds a provider interface while keeping demo mode as the default:

- FastAPI backend structure
- `/health` endpoint
- typed settings file
- SQLAlchemy database connection foundation
- SQLAlchemy models for customers, products, orders, order items, refunds, query logs, and feedback
- deterministic demo seed script
- analytics endpoints for top products, monthly revenue, refund rate, and customer segments
- `/validate-sql` endpoint for read-only SQL safety checks
- `/chat` endpoint with provider-based query generation, validation, execution, simple explanations, and query logging
- query log endpoints for reviewing recent chat interactions
- feedback endpoints linked to query logs
- evaluation cases for normal, unsupported, and unsafe questions
- evaluation endpoints for listing cases and running the suite
- demo query provider that runs without external services
- Docker Compose setup for backend and PostgreSQL
- tests for health, model registration, route registration, SQL validation, demo chat routing, query logs, feedback, evaluation, and the demo provider
- GitHub Actions workflow for backend tests

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
        queries.py
    core/
      config.py
      database.py
    demo/
      evaluation_questions.py
      seed_data.py
    models/
      database_models.py
      schemas.py
    providers/
      base.py
      demo_provider.py
      factory.py
    services/
      analytics_service.py
      chat_service.py
      demo_sql_generation_service.py
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
    test_provider.py
    test_query_logs_feedback.py
    test_sql_validation.py
docs/
  api_examples.md
  database_schema.md
```

The project is intentionally kept small. Each milestone should be easy to run, test, and explain.

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

The seed data is small on purpose. It is meant to support analytics endpoint development and manual demos without using private data.

## Testing

Run backend tests locally from the repository root:

```bash
cd backend
python -m pytest
```

GitHub Actions also runs the backend test workflow on pull requests.

## Provider Interface

For now, QueryPilot uses a demo provider that maps known business questions to SQL templates. I kept it this way on purpose so the project can run locally without external services.

The provider interface makes it easier to add a real LLM later, while still keeping SQL validation as a required safety step.

The default provider is configured with:

```text
QUERY_PROVIDER=demo
```

## Evaluation

The project includes a small evaluation suite for the demo agent.

Since this project is about safe Text-to-SQL, I do not want to only test happy paths. The evaluation cases include normal business questions, unsupported questions, and unsafe questions.

The suite checks whether known business questions are mapped to the expected query category, whether unsupported questions are handled cleanly, and whether unsafe questions are blocked.

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
GET  /queries/logs
GET  /queries/logs/{query_log_id}
POST /feedback
GET  /feedback/query/{query_log_id}
GET  /evaluation/cases
POST /evaluation/run
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

## Current Status

Safe demo Text-to-SQL backend:

- demo provider as the default query provider
- safe SQL validation
- analytics endpoints
- query history
- feedback
- evaluation suite

## Roadmap

### Next Milestone

Future LLM provider:

- keep demo provider as default
- add a real provider behind the interface
- no API key required for the basic demo
- SQL validation remains mandatory before execution

### Later

Schema-aware generation:

- expose database schema to the agent
- make the agent aware of table names, columns, and relationships
- still validate every SQL query before execution

Small UI or docs demo:

- screenshots
- example questions
- simple API walkthrough
- maybe a lightweight demo page only if the backend is stable
