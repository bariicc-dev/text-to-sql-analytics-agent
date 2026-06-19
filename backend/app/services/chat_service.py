from sqlalchemy.orm import Session

from app.models.schemas import ChatResponse
from app.providers.demo_provider import FALLBACK_MESSAGE
from app.providers.factory import get_query_provider
from app.services.explanation_service import explain_result
from app.services.logging_service import create_query_log
from app.services.query_execution_service import execute_read_query
from app.services.sql_validation_service import validate_sql

_NO_MATCH_MESSAGE = "No demo query matched this question."
_EXECUTION_ERROR_MESSAGE = "The query could not be executed safely."


def answer_question(question: str, db: Session) -> ChatResponse:
    candidate = get_query_provider().generate_query(question)
    if candidate.sql is None:
        reason = candidate.reason or _NO_MATCH_MESSAGE
        create_query_log(
            db=db,
            question=question,
            generated_sql=None,
            safety_status=candidate.safety_status,
            error_message=reason,
        )
        return ChatResponse(
            answer=FALLBACK_MESSAGE,
            sql=None,
            rows=[],
            explanation=reason,
            safety_status=candidate.safety_status,
            source=candidate.source,
        )

    validation = validate_sql(candidate.sql)
    if not validation.is_safe:
        create_query_log(
            db=db,
            question=question,
            generated_sql=validation.normalized_sql,
            safety_status="blocked",
            error_message=validation.reason,
        )
        return ChatResponse(
            answer="The generated SQL was blocked by the safety layer.",
            sql=validation.normalized_sql,
            rows=[],
            explanation=validation.reason,
            safety_status="blocked",
            source=candidate.source,
        )

    try:
        rows = execute_read_query(db=db, sql=validation.normalized_sql)
    except Exception:
        create_query_log(
            db=db,
            question=question,
            generated_sql=validation.normalized_sql,
            safety_status="error",
            error_message=_EXECUTION_ERROR_MESSAGE,
        )
        return ChatResponse(
            answer=_EXECUTION_ERROR_MESSAGE,
            sql=validation.normalized_sql,
            rows=[],
            explanation=_EXECUTION_ERROR_MESSAGE,
            safety_status="error",
            source=candidate.source,
        )

    create_query_log(
        db=db,
        question=question,
        generated_sql=validation.normalized_sql,
        safety_status="safe",
        error_message=None,
    )
    explanation = explain_result(question=question, rows=rows)

    return ChatResponse(
        answer=explanation,
        sql=validation.normalized_sql,
        rows=rows,
        explanation=explanation,
        safety_status="safe",
        source=candidate.source,
    )
