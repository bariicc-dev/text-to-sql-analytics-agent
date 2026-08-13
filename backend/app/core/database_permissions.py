from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schema_context.catalog import ANALYTICS_TABLE_NAMES

GENERATED_QUERY_ROLE = "querypilot_reader"


def apply_generated_query_permissions(session: Session) -> None:
    if session.bind is None or session.bind.dialect.name != "postgresql":
        return

    tables = ", ".join(f"public.{table_name}" for table_name in ANALYTICS_TABLE_NAMES)
    session.execute(
        text(
            f"REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public "
            f"FROM {GENERATED_QUERY_ROLE}"
        )
    )
    session.execute(
        text(
            f"REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public "
            f"FROM {GENERATED_QUERY_ROLE}"
        )
    )
    session.execute(text(f"GRANT USAGE ON SCHEMA public TO {GENERATED_QUERY_ROLE}"))
    session.execute(text(f"GRANT SELECT ON TABLE {tables} TO {GENERATED_QUERY_ROLE}"))
    session.commit()
