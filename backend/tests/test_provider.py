import pytest

from app.providers.demo_provider import DemoQueryProvider
from app.providers.factory import UnknownQueryProviderError, get_query_provider


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


def test_provider_factory_rejects_unknown_provider() -> None:
    with pytest.raises(UnknownQueryProviderError, match="Unknown query provider"):
        get_query_provider("missing")
