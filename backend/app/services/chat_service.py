from sqlalchemy.orm import Session

from app.models.schemas import ChatResponse
from app.services.demo_sql_generation_service import FALLBACK_MESSAGE, generate_demo_sql
from app.services.explanation_service import explain_result
from app.services.query_execution_service import execute_read_query
from app.services.sql_validation_service import validate_sql


def answer_question(question: str, db: Session) -> ChatResponse:
    demo_query = generate_demo_sql(question)
    if demo_query is None:
        return ChatResponse(
            answer=FALLBACK_MESSAGE,
            sql=None,
            rows=[],
            explanation="No demo query matched this question.",
            safety_status="not_generated",
            source="demo",
        )

    validation = validate_sql(demo_query.sql)
    if not validation.is_safe:
        return ChatResponse(
            answer="The generated SQL was blocked by the safety layer.",
            sql=validation.normalized_sql,
            rows=[],
            explanation=validation.reason,
            safety_status="blocked",
            source=demo_query.source,
        )

    rows = execute_read_query(db=db, sql=validation.normalized_sql)
    explanation = explain_result(question=question, rows=rows)

    return ChatResponse(
        answer=explanation,
        sql=validation.normalized_sql,
        rows=rows,
        explanation=explanation,
        safety_status="safe",
        source=demo_query.source,
    )
