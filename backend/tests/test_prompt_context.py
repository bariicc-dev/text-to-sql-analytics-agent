from fastapi.testclient import TestClient

from app.main import app
from app.prompting.builder import build_sql_prompt
from app.providers.llm_provider import LLMQueryProvider

client = TestClient(app)


def test_prompt_context_includes_user_question() -> None:
    question = "What are the top 5 products by revenue?"

    prompt = build_sql_prompt(question)

    assert question in prompt


def test_prompt_context_includes_compact_schema_tables() -> None:
    prompt = build_sql_prompt("Show monthly revenue.")

    assert "products(" in prompt
    assert "orders(" in prompt
    assert "order_items.product_id -> products.id" in prompt


def test_prompt_context_includes_safety_rules() -> None:
    prompt = build_sql_prompt("Show monthly revenue.")

    assert "Safe query rules:" in prompt
    assert "Use only SELECT or WITH" in prompt
    assert "Do not use INSERT" in prompt


def test_prompt_context_warns_against_unknown_columns() -> None:
    prompt = build_sql_prompt("Show monthly revenue.")

    assert "Do not guess table or column names" in prompt


def test_prompt_context_includes_expected_response_format() -> None:
    prompt = build_sql_prompt("Show monthly revenue.")

    assert '"category"' in prompt
    assert '"sql"' in prompt
    assert '"reason"' in prompt


def test_prompt_context_endpoint_returns_prompt() -> None:
    question = "Which customer segment brings the most revenue?"

    response = client.post("/prompt/context", json={"question": question})

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == question
    assert question in data["prompt"]
    assert "Expected JSON response:" in data["prompt"]


def test_llm_provider_can_build_prompt_context() -> None:
    prompt = LLMQueryProvider().build_prompt_context("What is the refund rate?")

    assert "What is the refund rate?" in prompt
    assert "refunds(" in prompt


def test_chat_route_still_exists_for_demo_provider() -> None:
    paths = {route.path for route in app.routes}

    assert "/chat" in paths


def test_evaluation_run_still_works_with_demo_provider() -> None:
    response = client.post("/evaluation/run")

    assert response.status_code == 200
    assert response.json()["failed"] == 0
