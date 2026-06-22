from app.main import app
from app.providers.demo_provider import DemoQueryProvider, FALLBACK_MESSAGE


def test_chat_route_is_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/chat" in paths


def test_demo_provider_returns_top_products_query() -> None:
    candidate = DemoQueryProvider().generate_query("What are the top 5 products by revenue?")

    assert candidate.category == "top_products"
    assert candidate.sql is not None
    assert "FROM products" in candidate.sql
    assert "LIMIT 5" in candidate.sql


def test_demo_provider_returns_monthly_revenue_query() -> None:
    candidate = DemoQueryProvider().generate_query("What is the monthly revenue trend?")

    assert candidate.category == "monthly_revenue"
    assert candidate.sql is not None
    assert "EXTRACT(MONTH" in candidate.sql


def test_demo_provider_returns_no_sql_for_unsupported_question() -> None:
    candidate = DemoQueryProvider().generate_query("Which warehouse is slowest?")

    assert candidate.sql is None
    assert candidate.safety_status == "not_generated"
    assert "demo mode" in FALLBACK_MESSAGE
