from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import GeneratedQuerySessionLocal


class GeneratedQueryExecutionError(Exception):
    pass


class GeneratedQueryTimeoutError(GeneratedQueryExecutionError):
    pass


class GeneratedQueryResultLimitError(GeneratedQueryExecutionError):
    pass


def execute_read_query(sql: str) -> list[dict[str, Any]]:
    settings = get_settings()

    try:
        with GeneratedQuerySessionLocal() as session:
            with session.begin():
                _configure_transaction(session, settings.generated_query_timeout_ms)
                result = session.execute(text(sql)).mappings()
                rows = result.fetchmany(settings.generated_query_max_rows + 1)
                if len(rows) > settings.generated_query_max_rows:
                    raise GeneratedQueryResultLimitError
    except DBAPIError as error:
        if _is_statement_timeout(error):
            raise GeneratedQueryTimeoutError from None
        raise GeneratedQueryExecutionError from None
    except SQLAlchemyError:
        raise GeneratedQueryExecutionError from None

    return [dict(row) for row in rows]


def _configure_transaction(session: Session, timeout_ms: int) -> None:
    if session.bind is None or session.bind.dialect.name != "postgresql":
        return

    session.execute(text("SET TRANSACTION READ ONLY"))
    session.execute(text("SET LOCAL search_path TO public"))
    session.execute(text(f"SET LOCAL statement_timeout = '{timeout_ms}ms'"))


def _is_statement_timeout(error: DBAPIError) -> bool:
    sqlstate = getattr(error.orig, "sqlstate", None) or getattr(error.orig, "pgcode", None)
    return sqlstate == "57014"
