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

## What It Does Now

Milestone 3 adds the SQL safety validation layer:

- FastAPI backend structure
- `/health` endpoint
- typed settings file
- SQLAlchemy database connection foundation
- SQLAlchemy models for customers, products, orders, order items, refunds, query logs, and feedback
- deterministic demo seed script
- analytics endpoints for top products, monthly revenue, refund rate, and customer segments
- `/validate-sql` endpoint for read-only SQL safety checks
- Docker Compose setup for backend and PostgreSQL
- tests for health, model registration, route registration, and SQL validation
- CI workflow skeleton

## Architecture

```text
backend/
  app/
    main.py
    api/
      routes/
        analytics.py
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
      sql_validation_service.py
  tests/
    test_analytics_routes.py
    test_database_models.py
    test_health.py
    test_sql_validation.py
docs/
  api_examples.md
  database_schema.md
```

Planned modules will add schema services, query execution, logging, feedback endpoints, and demo question mapping as the project grows.

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

## Run Tests

```bash
cd backend
pytest
```

## Example Questions

- What are the top 5 products by revenue?
- What is the monthly revenue trend?
- Which customer segment generates the most revenue?
- What is the refund rate by product category?
- Which products have high revenue but also high refunds?

## Current API

```text
GET  /health
POST /validate-sql
GET  /analytics/top-products
GET  /analytics/monthly-revenue
GET  /analytics/refund-rate
GET  /analytics/customer-segments
```

Planned endpoints:

```text
POST /chat
GET  /queries/logs
POST /feedback
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

Milestone 3 is complete: the backend foundation, synthetic database model layer, analytics endpoints, and SQL validation layer are in place. The next milestone is demo text-to-SQL chat.

## Roadmap

1. Demo database with customers, products, orders, order items, refunds, query logs, and feedback.
2. Analytics endpoints for top products, monthly revenue, refund rate, and customer segments.
3. SQL validation with clear safety reasons.
4. Demo text-to-SQL chat flow without requiring an external API key.
5. Query logs and feedback endpoints.
6. Evaluation suite with demo business questions.
7. Provider interface for future model integration while keeping demo mode as the default.
