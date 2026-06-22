from app.schema_context.catalog import DEMO_SCHEMA_CONTEXT
from app.schema_context.models import SchemaContext, TableContext


TABLE_CONTEXT_BY_NAME = {table.name: table for table in DEMO_SCHEMA_CONTEXT.tables}


def get_schema_context() -> SchemaContext:
    return DEMO_SCHEMA_CONTEXT


def get_table_context(table_name: str) -> TableContext | None:
    return TABLE_CONTEXT_BY_NAME.get(table_name.lower().strip())


def get_compact_schema_context() -> str:
    table_lines = [_format_table(table) for table in DEMO_SCHEMA_CONTEXT.tables]
    relationship_lines = sorted(
        {
            relationship
            for table in DEMO_SCHEMA_CONTEXT.tables
            for relationship in table.relationships
        }
    )

    sections = [
        f"Database: {DEMO_SCHEMA_CONTEXT.database_name}",
        "",
        "Tables:",
        *table_lines,
        "",
        "Relationships:",
        *(f"* {relationship}" for relationship in relationship_lines),
        "",
        "Safe query rules:",
        *(f"* {rule}" for rule in DEMO_SCHEMA_CONTEXT.safe_query_rules),
    ]
    return "\n".join(sections)


def _format_table(table: TableContext) -> str:
    column_names = ", ".join(column.name for column in table.columns)
    return f"* {table.name}({column_names})"
