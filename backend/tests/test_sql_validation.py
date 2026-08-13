import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.sql_validation_service import validate_sql

client = TestClient(app)


def test_validate_sql_endpoint_returns_validation_result() -> None:
    response = client.post(
        "/validate-sql",
        json={"sql": "SELECT id, name FROM products LIMIT 5"},
    )

    assert response.status_code == 200
    assert response.json()["is_safe"] is True


def test_allows_select_query() -> None:
    result = validate_sql("  SELECT id, name FROM products LIMIT 5  ")

    assert result.is_safe is True
    assert result.normalized_sql == "SELECT id, name FROM products LIMIT 5"


def test_allows_with_query() -> None:
    result = validate_sql("WITH revenue AS (SELECT 1) SELECT * FROM revenue LIMIT 10")

    assert result.is_safe is True


def test_blocks_update_statement() -> None:
    result = validate_sql("UPDATE products SET name = 'x'")

    assert result.is_safe is False
    assert "UPDATE" in result.blocked_keywords


def test_blocks_multiple_statements() -> None:
    result = validate_sql("SELECT id FROM products; DROP TABLE products")

    assert result.is_safe is False
    assert result.reason == "Multiple SQL statements are not allowed."


def test_blocks_sql_comments() -> None:
    result = validate_sql("SELECT id FROM products -- ignore filters")

    assert result.is_safe is False
    assert result.reason == "SQL comments are not allowed in submitted queries."


def test_blocks_select_star_without_limit() -> None:
    result = validate_sql("SELECT * FROM customers")

    assert result.is_safe is False
    assert result.reason == "SELECT * queries must include a reasonable LIMIT."


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT id INTO copied_products FROM products",
        "SELECT id FROM products FOR UPDATE",
        "SELECT id FROM products FOR SHARE",
        "WITH changed AS (UPDATE products SET name = 'x' RETURNING id) SELECT id FROM changed",
    ],
)
def test_blocks_write_or_locking_select_variants(sql: str) -> None:
    assert validate_sql(sql).is_safe is False


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT id FROM query_logs LIMIT 5",
        "SELECT id FROM feedback LIMIT 5",
        "SELECT tablename FROM pg_catalog.pg_tables LIMIT 5",
        "SELECT table_name FROM information_schema.tables LIMIT 5",
        "SELECT id FROM private.products LIMIT 5",
        "SELECT id FROM private.unlisted_table LIMIT 5",
    ],
)
def test_blocks_internal_tables_and_unapproved_schemas(sql: str) -> None:
    assert validate_sql(sql).is_safe is False


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT pg_read_file('/tmp/data')",
        "SELECT pg_ls_dir('/tmp')",
        "SELECT pg_terminate_backend(1)",
        "SELECT set_config('search_path', 'pg_catalog', false)",
    ],
)
def test_blocks_administrative_functions(sql: str) -> None:
    assert validate_sql(sql).is_safe is False


def test_allows_public_analytics_table_reference() -> None:
    result = validate_sql("SELECT id FROM public.products LIMIT 5")

    assert result.is_safe is True
