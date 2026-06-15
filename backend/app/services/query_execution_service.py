from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def execute_read_query(db: Session, sql: str) -> list[dict[str, Any]]:
    rows = db.execute(text(sql)).mappings().all()
    return [dict(row) for row in rows]
