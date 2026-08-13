from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.core.database import (
    ApplicationSessionLocal,
    GeneratedQuerySessionLocal,
    application_engine,
    generated_query_engine,
)
from app.services import query_execution_service
from app.services.query_execution_service import (
    GeneratedQueryExecutionError,
    GeneratedQueryResultLimitError,
    GeneratedQueryTimeoutError,
    execute_read_query,
)


def test_database_sessions_use_distinct_configured_identities() -> None:
    assert application_engine.url.username == "querypilot_app"
    assert generated_query_engine.url.username == "querypilot_reader"
    assert ApplicationSessionLocal.kw["bind"] is application_engine
    assert GeneratedQuerySessionLocal.kw["bind"] is generated_query_engine


@pytest.mark.parametrize(
    "field_and_value",
    [
        {"generated_query_timeout_ms": 99},
        {"generated_query_timeout_ms": 30_001},
        {"generated_query_max_rows": 0},
        {"generated_query_max_rows": 1_001},
    ],
)
def test_generated_query_limits_are_validated(field_and_value: dict[str, int]) -> None:
    with pytest.raises(ValidationError):
        Settings(**field_and_value)


def test_executor_raises_when_result_exceeds_configured_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE products (id INTEGER PRIMARY KEY)"))
        connection.execute(text("INSERT INTO products (id) VALUES (1), (2), (3)"))

    reader_session = sessionmaker(bind=engine)
    monkeypatch.setattr(query_execution_service, "GeneratedQuerySessionLocal", reader_session)
    monkeypatch.setattr(
        query_execution_service,
        "get_settings",
        lambda: SimpleNamespace(
            generated_query_timeout_ms=5_000,
            generated_query_max_rows=2,
        ),
    )

    with pytest.raises(GeneratedQueryResultLimitError):
        execute_read_query("SELECT id FROM products ORDER BY id")


@pytest.mark.parametrize(
    ("sqlstate", "expected_error"),
    [
        ("57014", GeneratedQueryTimeoutError),
        ("42501", GeneratedQueryExecutionError),
    ],
)
def test_executor_translates_database_errors(
    sqlstate: str,
    expected_error: type[GeneratedQueryExecutionError],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DriverError(Exception):
        pass

    driver_error = DriverError("private database details")
    driver_error.sqlstate = sqlstate  # type: ignore[attr-defined]

    class Transaction:
        def __enter__(self) -> None:
            return None

        def __exit__(self, *args: object) -> None:
            return None

    class TimeoutSession:
        bind = SimpleNamespace(dialect=SimpleNamespace(name="sqlite"))

        def __enter__(self) -> "TimeoutSession":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def begin(self) -> Transaction:
            return Transaction()

        def execute(self, statement: object) -> None:
            raise OperationalError(str(statement), {}, driver_error)

    monkeypatch.setattr(
        query_execution_service,
        "GeneratedQuerySessionLocal",
        TimeoutSession,
    )

    with pytest.raises(expected_error):
        execute_read_query("SELECT pg_sleep(10)")


def test_postgresql_reader_transaction_is_configured_before_query() -> None:
    statements: list[str] = []

    class Result:
        def mappings(self) -> "Result":
            return self

        def fetchmany(self, size: int) -> list[dict[str, object]]:
            return []

    class ReaderSession:
        bind = SimpleNamespace(dialect=SimpleNamespace(name="postgresql"))

        def execute(self, statement: object) -> Result:
            statements.append(str(statement))
            return Result()

    query_execution_service._configure_transaction(ReaderSession(), 2_500)  # type: ignore[arg-type]

    assert statements == [
        "SET TRANSACTION READ ONLY",
        "SET LOCAL search_path TO public",
        "SET LOCAL statement_timeout = '2500ms'",
    ]
