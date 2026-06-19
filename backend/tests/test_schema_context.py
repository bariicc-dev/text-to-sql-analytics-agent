from fastapi.testclient import TestClient

from app.main import app
from app.schema_context.service import get_compact_schema_context, get_schema_context, get_table_context

client = TestClient(app)


def test_read_schema_returns_database_name_and_tables() -> None:
    response = client.get("/schema")

    assert response.status_code == 200
    data = response.json()
    assert data["database_name"] == "demo_ecommerce"
    assert len(data["tables"]) >= 7


def test_schema_includes_core_tables() -> None:
    schema = get_schema_context()

    table_names = {table.name for table in schema.tables}

    assert {"customers", "products", "orders", "order_items", "refunds", "query_logs", "feedback"}.issubset(table_names)


def test_read_products_table_context() -> None:
    response = client.get("/schema/tables/products")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "products"
    assert data["primary_key"] == "id"
    assert any(column["name"] == "category" for column in data["columns"])


def test_read_unknown_table_returns_404() -> None:
    response = client.get("/schema/tables/unknown_table")

    assert response.status_code == 404
    assert response.json()["detail"] == "Table context not found."


def test_compact_schema_context_contains_tables_and_relationships() -> None:
    response = client.get("/schema/compact")

    assert response.status_code == 200
    context = response.json()["context"]
    assert "products(" in context
    assert "orders.customer_id -> customers.id" in context
    assert "order_items.product_id -> products.id" in context


def test_get_table_context_returns_none_for_missing_table() -> None:
    assert get_table_context("missing") is None


def test_compact_schema_service_mentions_safe_query_rules() -> None:
    context = get_compact_schema_context()

    assert "Safe query rules:" in context
    assert "Generated SQL must be validated before execution." in context


def test_chat_route_still_exists() -> None:
    paths = {route.path for route in app.routes}

    assert "/chat" in paths


def test_evaluation_run_still_works() -> None:
    response = client.post("/evaluation/run")

    assert response.status_code == 200
    data = response.json()
    assert data["total_cases"] > 0
    assert data["failed"] == 0
