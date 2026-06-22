from pydantic import BaseModel, Field


class ColumnContext(BaseModel):
    name: str
    type: str
    description: str
    is_nullable: bool
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: str | None = None


class TableContext(BaseModel):
    name: str
    description: str
    columns: list[ColumnContext]
    primary_key: str
    relationships: list[str] = Field(default_factory=list)


class SchemaContext(BaseModel):
    database_name: str
    description: str
    tables: list[TableContext]
    safe_query_rules: list[str] = Field(default_factory=list)
