import pytest

from app.providers.demo_provider import DemoQueryProvider
from app.providers.factory import UnknownQueryProviderError, get_query_provider
from app.providers.llm_provider import LLMQueryProvider
from app.schema_context.service import get_schema_context


def test_default_provider_is_demo() -> None:
    provider = get_query_provider()

    assert isinstance(provider, DemoQueryProvider)


def test_demo_provider_returns_top_products_category() -> None:
    provider = DemoQueryProvider()

    candidate = provider.generate_query("What are the top 5 products by revenue?")

    assert candidate.category == "top_products"
    assert candidate.sql is not None
    assert candidate.source == "demo"


def test_demo_provider_returns_monthly_revenue_category() -> None:
    provider = DemoQueryProvider()

    candidate = provider.generate_query("Show me monthly revenue.")

    assert candidate.category == "monthly_revenue"
    assert candidate.sql is not None


def test_demo_provider_accepts_optional_schema_context() -> None:
    provider = DemoQueryProvider()

    candidate = provider.generate_query("Show me monthly revenue.", schema_context=get_schema_context())

    assert candidate.category == "monthly_revenue"
    assert candidate.sql is not None


def test_demo_provider_returns_unsupported_for_unknown_question() -> None:
    provider = DemoQueryProvider()

    candidate = provider.generate_query("Give me employee salaries.")

    assert candidate.category == "unsupported"
    assert candidate.sql is None
    assert candidate.safety_status == "not_generated"


def test_demo_provider_marks_unsafe_question_as_blocked() -> None:
    provider = DemoQueryProvider()

    candidate = provider.generate_query("Delete all orders.")

    assert candidate.category == "unsupported"
    assert candidate.sql is None
    assert candidate.safety_status == "blocked"


def test_provider_factory_returns_demo_provider() -> None:
    provider = get_query_provider("demo")

    assert isinstance(provider, DemoQueryProvider)


def test_provider_factory_returns_llm_provider_without_api_key() -> None:
    provider = get_query_provider("llm")

    assert isinstance(provider, LLMQueryProvider)


def test_llm_provider_returns_not_configured_candidate() -> None:
    provider = LLMQueryProvider()

    candidate = provider.generate_query("What are the top products?", schema_context=get_schema_context())

    assert candidate.category == "unsupported"
    assert candidate.sql is None
    assert candidate.source == "llm"
    assert candidate.safety_status == "not_generated"
    assert candidate.reason == "LLM provider is not configured yet. Use QUERY_PROVIDER=demo. Schema context will be used by this provider later."


def test_provider_factory_rejects_unknown_provider() -> None:
    with pytest.raises(UnknownQueryProviderError, match="Unknown query provider"):
        get_query_provider("missing")
