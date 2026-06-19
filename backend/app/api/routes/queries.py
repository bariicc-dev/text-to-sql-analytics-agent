from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import QueryLogRead, SqlValidationRequest, SqlValidationResponse
from app.services.logging_service import get_query_log, list_query_logs
from app.services.sql_validation_service import validate_sql

router = APIRouter(tags=["queries"])


@router.post("/validate-sql", response_model=SqlValidationResponse)
def validate_sql_query(request: SqlValidationRequest) -> SqlValidationResponse:
    return validate_sql(request.sql)


@router.get("/queries/logs", response_model=list[QueryLogRead])
def read_query_logs(
    limit: int = Query(default=20, ge=1, le=100),
    safety_status: str | None = None,
    db: Session = Depends(get_db),
) -> list[QueryLogRead]:
    return list_query_logs(db=db, limit=limit, safety_status=safety_status)


@router.get("/queries/logs/{query_log_id}", response_model=QueryLogRead)
def read_query_log(query_log_id: int, db: Session = Depends(get_db)) -> QueryLogRead:
    query_log = get_query_log(db=db, query_log_id=query_log_id)
    if query_log is None:
        raise HTTPException(status_code=404, detail="Query log not found.")

    return query_log
