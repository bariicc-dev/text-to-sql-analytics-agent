from app.main import app
from app.services.demo_sql_generation_service import FALLBACK_MESSAGE, generate_demo_sql


def test_chat_route_is_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/chat" in paths


def test_demo_sql_generation_for_top_products() -> None:
    query = generate_demo_sql("What are the top 5 products by revenue?")

    assert query is not None
    assert "FROM products" in query.sql
    assert "LIMIT 5" in query.sql


def test_demo_sql_generation_for_monthly_revenue() -> None:
    query = generate_demo_sql("What is the monthly revenue trend?")

    assert query is not None
    assert "EXTRACT(MONTH" in query.sql


def test_demo_sql_generation_fallback() -> None:
    query = generate_demo_sql("Which warehouse is slowest?")

    assert query is None
    assert "demo mode" in FALLBACK_MESSAGE
