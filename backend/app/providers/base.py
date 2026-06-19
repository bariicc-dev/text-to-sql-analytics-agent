from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class QueryCandidate:
    category: str
    sql: str | None
    source: str
    confidence: float = 0.0
    reason: str | None = None
    safety_status: str = "not_checked"


class QueryProvider(Protocol):
    def generate_query(self, question: str, schema_context: Any | None = None) -> QueryCandidate:
        ...
