import json

import httpx
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app
from app.providers.demo_provider import DemoQueryProvider
from app.providers.factory import get_query_provider
from app.providers.llm_provider import LLMQueryProvider

client = TestClient(app)


def _nvidia_settings(**overrides: object) -> Settings:
    values = {
        "llm_provider": "nvidia",
        "llm_model": "test-model",
        "llm_api_base_url": "https://example.test/v1",
        "llm_api_key": "test-key",
    }
    values.update(overrides)
    return Settings(**values)


def test_demo_provider_still_works_without_llm_config() -> None:
    provider = get_query_provider("demo")

    candidate = provider.generate_query("What are the top 5 products by revenue?")

    assert isinstance(provider, DemoQueryProvider)
    assert candidate.category == "top_products"
    assert candidate.sql is not None


def test_llm_provider_returns_not_configured_result_when_config_missing() -> None:
    provider = LLMQueryProvider(settings=Settings(llm_provider="nvidia"))

    candidate = provider.generate_query("What are the top products?")

    assert candidate.category == "unsupported"
    assert candidate.sql is None
    assert candidate.safety_status == "not_generated"
    assert candidate.reason is not None
    assert "Missing" in candidate.reason


def test_nvidia_provider_builds_request_payload_from_prompt_context() -> None:
    provider = LLMQueryProvider(settings=_nvidia_settings())

    payload = provider.build_request_payload("What are the top 5 products by revenue?")

    assert payload["model"] == "test-model"
    assert payload["temperature"] == 0
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"
    user_prompt = payload["messages"][1]["content"]
    assert "What are the top 5 products by revenue?" in user_prompt
    assert "products(" in user_prompt
    assert "Expected JSON response:" in user_prompt


def test_nvidia_provider_parses_valid_json_response_into_candidate() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert str(request.url) == "https://example.test/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer test-key"
        assert payload["model"] == "test-model"
        assert "products(" in payload["messages"][1]["content"]
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "category": "top_products",
                                    "sql": "SELECT id, name FROM products LIMIT 5",
                                    "reason": "Product ranking question.",
                                }
                            )
                        }
                    }
                ]
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = LLMQueryProvider(settings=_nvidia_settings(), client=http_client)

    candidate = provider.generate_query("What are the top 5 products by revenue?")

    assert candidate.category == "top_products"
    assert candidate.sql == "SELECT id, name FROM products LIMIT 5"
    assert candidate.reason == "Product ranking question."
    assert candidate.safety_status == "not_checked"


def test_nvidia_provider_handles_invalid_json_response_safely() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "not json"}}]},
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = LLMQueryProvider(settings=_nvidia_settings(), client=http_client)

    candidate = provider.generate_query("What are the top products?")

    assert candidate.category == "unsupported"
    assert candidate.sql is None
    assert candidate.safety_status == "not_generated"
    assert candidate.reason == "LLM response was not valid JSON."


def test_chat_route_still_exists_with_demo_provider() -> None:
    paths = {route.path for route in app.routes}

    assert "/chat" in paths


def test_evaluation_run_still_works_with_demo_provider() -> None:
    response = client.post("/evaluation/run")

    assert response.status_code == 200
    assert response.json()["failed"] == 0
