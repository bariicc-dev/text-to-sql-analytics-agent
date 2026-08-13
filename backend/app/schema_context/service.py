from app.schema_context.catalog import ANALYTICS_TABLE_NAMES, DEMO_SCHEMA_CONTEXT
from app.schema_context.models import SchemaContext, TableContext


TABLE_CONTEXT_BY_NAME = {table.name: table for table in DEMO_SCHEMA_CONTEXT.tables}
ANALYTICS_TABLE_NAME_SET = set(ANALYTICS_TABLE_NAMES)


def get_schema_context() -> SchemaContext:
    return DEMO_SCHEMA_CONTEXT


def get_table_context(table_name: str) -> TableContext | None:
    return TABLE_CONTEXT_BY_NAME.get(table_name.lower().strip())


def get_compact_schema_context() -> str:
    analytics_tables = [
        table
        for table in DEMO_SCHEMA_CONTEXT.tables
        if table.name in ANALYTICS_TABLE_NAME_SET
    ]
    table_lines = [_format_table(table) for table in analytics_tables]
    relationship_lines = sorted(
        {
            relationship
            for table in analytics_tables
            for relationship in table.relationships
            if _uses_only_analytics_tables(relationship)
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


def _uses_only_analytics_tables(relationship: str) -> bool:
    table_names = {
        side.strip().split(".", maxsplit=1)[0]
        for side in relationship.split("->")
    }
    return table_names.issubset(ANALYTICS_TABLE_NAME_SET)
