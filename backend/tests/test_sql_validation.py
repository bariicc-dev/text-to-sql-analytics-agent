from app.main import app
from app.services.sql_validation_service import validate_sql


def test_validate_sql_route_is_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/validate-sql" in paths


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
