# API Examples

These examples assume the backend is running locally on port `8000` and the synthetic data has been seeded.

## Chat

Ask a question through the default demo provider:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the top 5 products by revenue?"}'
```

The response includes the answer, SQL, rows, explanation, safety status, and provider source. The interaction is saved in query history.

## Validate SQL

Check a SQL candidate without executing it:

```bash
curl -X POST http://localhost:8000/validate-sql \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT id, name FROM products LIMIT 5"}'
```

## Query logs and feedback

Read recent query logs:

```bash
curl "http://localhost:8000/queries/logs?limit=20"
```

Use a returned query log ID when creating feedback:

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"query_log_id":1,"rating":5,"comment":"Useful answer"}'
```

## Schema context

Read the compact schema context used for provider prompts:

```bash
curl http://localhost:8000/schema/compact
```

## Prompt context

Inspect the prompt context for a question:

```bash
curl -X POST http://localhost:8000/prompt/context \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the top 5 products by revenue?"}'
```

This endpoint returns the prepared context without calling an external model.

## Provider evaluation

Run all cases with the default demo provider:

```bash
curl -X POST http://localhost:8000/evaluation/run
```

Compare the demo and LLM providers with the same cases:

```bash
curl -X POST http://localhost:8000/evaluation/compare
```

If the LLM provider is not configured, its summary reports `not_configured` without calling an external API.

## Optional provider configuration

Demo mode is the default and does not require an API key:

```text
QUERY_PROVIDER=demo
```

The optional NVIDIA-compatible provider uses placeholders for user-supplied settings:

```text
QUERY_PROVIDER=llm
LLM_PROVIDER=nvidia
LLM_MODEL=<model-name>
LLM_API_BASE_URL=<nvidia-compatible-chat-completions-base-url>
LLM_API_KEY=<your-api-key>
```
