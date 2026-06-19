from typing import Any

from app.providers.base import QueryCandidate

_NOT_CONFIGURED_MESSAGE = "LLM provider is not configured yet. Use QUERY_PROVIDER=demo. Schema context will be used by this provider later."


class LLMQueryProvider:
    source = "llm"

    def generate_query(self, question: str, schema_context: Any | None = None) -> QueryCandidate:
        return QueryCandidate(
            category="unsupported",
            sql=None,
            source=self.source,
            confidence=0.0,
            reason=_NOT_CONFIGURED_MESSAGE,
            safety_status="not_generated",
        )
