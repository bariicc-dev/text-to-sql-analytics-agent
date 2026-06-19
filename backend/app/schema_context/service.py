from app.schema_context.catalog import DEMO_SCHEMA_CONTEXT
from app.schema_context.models import SchemaContext, TableContext


def get_schema_context() -> SchemaContext:
    return DEMO_SCHEMA_CONTEXT


def get_table_context(table_name: str) -> TableContext | None:
    normalized_name = table_name.lower().strip()
    for table in DEMO_SCHEMA_CONTEXT.tables:
        if table.name == normalized_name:
            return table
    return None


def get_compact_schema_context() -> str:
    table_lines = []
    relationship_lines = []

    for table in DEMO_SCHEMA_CONTEXT.tables:
        column_names = ", ".join(column.name for column in table.columns)
        table_lines.append(f"* {table.name}({column_names})")
        relationship_lines.extend(f"* {relationship}" for relationship in table.relationships)

    sections = [
        f"Database: {DEMO_SCHEMA_CONTEXT.database_name}",
        "",
        "Tables:",
        *table_lines,
        "",
        "Relationships:",
        *relationship_lines,
        "",
        "Safe query rules:",
        *(f"* {rule}" for rule in DEMO_SCHEMA_CONTEXT.safe_query_rules),
    ]
    return "\n".join(sections)
