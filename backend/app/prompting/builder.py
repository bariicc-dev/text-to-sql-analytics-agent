from app.schema_context.service import get_compact_schema_context

_EXPECTED_OUTPUT_FORMAT = """{
  "category": "short_category_name",
  "sql": "SELECT ...",
  "reason": "short explanation"
}"""


def build_sql_prompt(question: str) -> str:
    cleaned_question = question.strip()
    schema_context = get_compact_schema_context()

    sections = [
        "Build one safe SQL query for the demo e-commerce database.",
        "",
        "User question:",
        cleaned_question,
        "",
        "Schema context:",
        schema_context,
        "",
        "Instructions:",
        "- Return only one SQL query in the sql field.",
        "- Use only SELECT or WITH queries.",
        "- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, or other data modification statements.",
        "- Do not guess table or column names that are not in the schema context.",
        "- Keep the reason short.",
        "",
        "Expected JSON response:",
        _EXPECTED_OUTPUT_FORMAT,
    ]
    return "\n".join(sections)
