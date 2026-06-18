# QueryPilot: Safe Text-to-SQL Analytics Agent

QueryPilot is a personal Data & AI Engineering project where I am building a safe analytics agent that can answer business questions using SQL.

The goal is not just to generate SQL. The goal is to make the workflow safer, more transparent, and easier to evaluate.

I am building this project step by step to practice backend APIs, PostgreSQL, SQL validation, data modeling, and AI-assisted analytics workflows using only synthetic demo data.

## Why I Am Building It

Text-to-SQL can be useful, but it can also be risky if queries are generated and executed without checks. This project focuses on the controlled backend workflow around analytics questions:

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

Query logs and feedback are important because a Text-to-SQL agent should not be a black box. I want to track what was asked, what SQL was generated, whether it was safe, and whether the answer was useful.

## What It Does Now

Milestone 5 adds query history, a feedback endpoint, and logged chat interactions:

- FastAPI backend structure
- `/health` endpoint
- typed settings file
- SQLAlchemy database connection foundation
- SQLAlchemy models for customers, products, orders, order items, refunds, query logs, and feedback
- deterministic demo seed script
- analytics endpoints for top products, monthly revenue, refund rate, and customer segments
- `/validate-sql` endpoint for read-only SQL safety checks
- `/chat` endpoint with demo question mapping, validation, execution, simple explanations, and query logging
- query log endpoints for reviewing recent chat interactions
- feedback endpoints linked to query logs
- Docker Compose setup for backend and PostgreSQL
- tests for health, model registration, route registration, SQL validation, demo chat routing, query logs, and feedback
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
        feedback.py
        health.py
        queries.py
    core/
      config.py
      database.py
    demo/
      seed_data.py
    models/
      database_models.py
      schemas.py
    services/
      analytics_service.py
      chat_service.py
      demo_sql_generation_service.py
      explanation_service.py
      feedback_service.py
      logging_service.py
      query_execution_service.py
      sql_validation_service.py
  tests/
    test_analytics_routes.py
    test_chat.py
    test_database_models.py
    test_health.py
    test_query_logs_feedback.py
    test_sql_validation.py
docs/
  api_examples.md
  database_schema.md
```

Planned modules will add evaluation and a provider interface while keeping demo mode as the default.

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

Milestone 5 is complete: chat interactions are logged, recent query logs can be reviewed, and feedback can be attached to a query log. The next milestone is evaluation with demo business questions.

## Roadmap

1. Demo database with customers, products, orders, order items, refunds, query logs, and feedback.
2. Analytics endpoints for top products, monthly revenue, refund rate, and customer segments.
3. SQL validation with clear safety reasons.
4. Demo text-to-SQL chat flow without requiring an external API key.
5. Query logs and feedback endpoints.
6. Evaluation suite with demo business questions.
7. Provider interface for future model integration while keeping demo mode as the default.
