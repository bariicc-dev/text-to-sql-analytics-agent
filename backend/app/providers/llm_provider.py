from typing import Any

from app.prompting.builder import build_sql_prompt
from app.providers.base import QueryCandidate

_NOT_CONFIGURED_MESSAGE = (
    "LLM provider is not configured yet. Use QUERY_PROVIDER=demo. "
    "Prompt context is ready for future provider calls."
)


class LLMQueryProvider:
    source = "llm"

    def build_prompt_context(self, question: str) -> str:
        return build_sql_prompt(question)

    def generate_query(self, question: str, schema_context: Any | None = None) -> QueryCandidate:
        return QueryCandidate(
            category="unsupported",
            sql=None,
            source=self.source,
            confidence=0.0,
            reason=_NOT_CONFIGURED_MESSAGE,
            safety_status="not_generated",
        )
