from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.database_models import QueryLog


def create_query_log(
    db: Session,
    question: str,
    generated_sql: str | None,
    safety_status: str,
    error_message: str | None = None,
) -> QueryLog:
    query_log = QueryLog(
        question=question,
        generated_sql=generated_sql,
        safety_status=safety_status,
        error_message=error_message,
    )
    db.add(query_log)
    db.commit()
    db.refresh(query_log)
    return query_log


def list_query_logs(
    db: Session,
    limit: int = 20,
    safety_status: str | None = None,
) -> list[QueryLog]:
    statement = select(QueryLog).order_by(desc(QueryLog.created_at), desc(QueryLog.id)).limit(limit)
    if safety_status is not None:
        statement = statement.where(QueryLog.safety_status == safety_status)

    return list(db.scalars(statement))


def get_query_log(db: Session, query_log_id: int) -> QueryLog | None:
    return db.get(QueryLog, query_log_id)
