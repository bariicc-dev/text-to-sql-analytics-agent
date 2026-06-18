from sqlalchemy.orm import Session

from app.models.schemas import ChatResponse
from app.services.demo_sql_generation_service import FALLBACK_MESSAGE, generate_demo_sql
from app.services.explanation_service import explain_result
from app.services.logging_service import create_query_log
from app.services.query_execution_service import execute_read_query
from app.services.sql_validation_service import validate_sql

_NO_MATCH_MESSAGE = "No demo query matched this question."
_EXECUTION_ERROR_MESSAGE = "The query could not be executed safely."


def answer_question(question: str, db: Session) -> ChatResponse:
    demo_query = generate_demo_sql(question)
    if demo_query is None:
        create_query_log(
            db=db,
            question=question,
            generated_sql=None,
            safety_status="not_generated",
            error_message=_NO_MATCH_MESSAGE,
        )
        return ChatResponse(
            answer=FALLBACK_MESSAGE,
            sql=None,
            rows=[],
            explanation=_NO_MATCH_MESSAGE,
            safety_status="not_generated",
            source="demo",
        )

    validation = validate_sql(demo_query.sql)
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
            source=demo_query.source,
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
            source=demo_query.source,
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
        source=demo_query.source,
    )
