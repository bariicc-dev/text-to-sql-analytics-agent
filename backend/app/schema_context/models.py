from pydantic import BaseModel, Field


class ColumnContext(BaseModel):
    name: str
    type: str
    description: str
    is_nullable: bool
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: str | None = None
    example_values: list[str] = Field(default_factory=list)


class TableContext(BaseModel):
    name: str
    description: str
    columns: list[ColumnContext]
    primary_key: str
    relationships: list[str] = Field(default_factory=list)
    common_questions: list[str] = Field(default_factory=list)


class SchemaContext(BaseModel):
    database_name: str
    description: str
    tables: list[TableContext]
    business_rules: list[str] = Field(default_factory=list)
    safe_query_rules: list[str] = Field(default_factory=list)
