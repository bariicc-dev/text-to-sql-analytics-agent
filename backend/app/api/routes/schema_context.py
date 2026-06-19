from fastapi import APIRouter, HTTPException

from app.schema_context.models import SchemaContext, TableContext
from app.schema_context.service import get_compact_schema_context, get_schema_context, get_table_context

router = APIRouter(prefix="/schema", tags=["schema"])


@router.get("", response_model=SchemaContext)
def read_schema_context() -> SchemaContext:
    return get_schema_context()


@router.get("/tables/{table_name}", response_model=TableContext)
def read_table_context(table_name: str) -> TableContext:
    table = get_table_context(table_name)
    if table is None:
        raise HTTPException(status_code=404, detail="Table context not found.")

    return table


@router.get("/compact")
def read_compact_schema_context() -> dict[str, str]:
    return {"context": get_compact_schema_context()}
