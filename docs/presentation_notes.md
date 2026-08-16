# QueryPilot presentation notes

## One-minute explanation

QueryPilot is a backend project that turns plain-language analytics questions into SQL while treating generated SQL as untrusted input. A provider produces a SQL candidate, the backend checks that it is a single read-only query, and only approved SQL is executed against a PostgreSQL database. The result is returned through a FastAPI API and the interaction is logged for review and feedback.

It is not just a chat endpoint. The project also includes schema and prompt context, interchangeable providers, SQL validation, query history, feedback, and an evaluation suite that checks how each provider behaves on supported, unsupported, and unsafe questions. The deterministic demo provider makes the complete flow repeatable without an API key, while the optional NVIDIA-compatible provider shows where a configured LLM can use the same safety path.

## Problem

Natural-language access to data is useful, but generated SQL should not be executed blindly. Common risks include:

- unsafe write or administrative SQL
- hallucinated tables or columns
- queries that are valid SQL but answer the wrong question
- no record of the question, generated SQL, or outcome
- no repeatable way to evaluate provider behavior

## Solution

QueryPilot separates query generation from validation and execution:

```text
Question
→ provider
→ SQL candidate
→ SQL validation
→ approved read-only execution
→ response
→ query log
→ feedback
→ provider evaluation
```

The provider can suggest SQL, but it cannot bypass the validation step. Evaluation runs the same cases across providers and records category matching, safety status, SQL generation, SQL validation, and pass or fail reasons.

## Architecture

- **FastAPI routes** expose chat, validation, history, feedback, schema context, prompt context, analytics, and evaluation endpoints.
- **PostgreSQL database** stores the synthetic e-commerce data, query logs, and feedback.
- **SQLAlchemy models** define database tables and manage database access.
- **Provider interface** gives the chat and evaluation services one contract for SQL candidates.
- **Demo provider** maps a small set of known analytics questions to deterministic SQL templates.
- **NVIDIA-compatible provider** optionally calls a configured chat-completions endpoint and parses a SQL candidate.
- **Schema context** describes available tables, columns, relationships, and business meaning.
- **Prompt context builder** combines the question, compact schema context, safety rules, and response format.
- **SQL validator** allows a single read-only `SELECT` or `WITH` query and blocks unsafe patterns.
- **Evaluation runner** applies the same cases to a selected provider or compares providers.
- **Query logs and feedback** preserve what happened and allow a result to be rated later.

The API routes remain thin; services own validation, execution, logging, and evaluation decisions.

## Libraries and why they are used

| Technology | Why it is used |
| --- | --- |
| FastAPI | Defines the HTTP API, validates requests, and provides interactive Swagger documentation. |
| PostgreSQL | Stores the e-commerce dataset, query history, and feedback, and executes approved analytics SQL. |
| SQLAlchemy | Defines database models and keeps database sessions and queries organized. |
| Pydantic | Defines typed request and response models and loads application settings. |
| Docker Compose | Starts the backend and PostgreSQL together with repeatable local configuration. |
| pytest | Runs the backend unit and API tests. |
| httpx | Sends requests to the optional NVIDIA-compatible endpoint; tests use its mock transport instead of external calls. |
| GitHub Actions | Installs the backend dependencies and runs pytest for repository checks. |

## Demo provider vs NVIDIA-compatible provider

### Demo provider

- deterministic and enabled by default
- maps known business questions to SQL templates
- runs without an API key or external service
- supports repeatable tests, demos, and evaluation

The SQL template is selected in code, but the returned analytics rows are not hardcoded. Approved SQL runs against the seeded PostgreSQL database.

### NVIDIA-compatible provider

- optional and enabled through local configuration
- requires a compatible endpoint, model name, and API key
- uses prompt context and schema context
- parses the model response into a SQL candidate
- sends that candidate through the same SQL validation step before execution

Provider generation and SQL safety are separate responsibilities. Configuring an LLM changes where the candidate comes from, not whether validation is required.

## What I learned / what this project shows

The project demonstrates:

- backend API design with small routes and service boundaries
- SQL safety checks before generated queries reach execution
- relational data modeling for analytics, logs, and feedback
- a provider abstraction that keeps demo and LLM paths consistent
- LLM integration design with explicit schema and prompt context
- an evaluation mindset for normal, unsupported, unsafe, and unconfigured cases
- automated testing without real external API calls
- Docker-based local setup
- documentation that explains how to run and inspect the system

## Current limitations

These are deliberate v1 scope choices:

- the dataset is synthetic and limited to one e-commerce schema
- the demo provider supports a small set of analytics questions
- real LLM behavior depends on the user's provider configuration and credentials
- v1 has no frontend
- the project is not deployed yet
- authentication and a multi-user production layer are not included

Generated SQL is validated before execution. A production version should also add database-level read-only credentials, tighter resource limits, authentication, and monitoring.

## Possible next improvements

- deploy the backend
- add a small dashboard or frontend
- expand the evaluation cases
- test the NVIDIA-compatible provider manually with credentials
- use a larger, more realistic dataset
- add charts for analytics results
- add a user-facing analytics interface

These are possible follow-up directions, not features included in v1.
