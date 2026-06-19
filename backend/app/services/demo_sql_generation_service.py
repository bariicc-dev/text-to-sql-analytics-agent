from app.providers.base import QueryCandidate
from app.providers.demo_provider import DemoQueryProvider, FALLBACK_MESSAGE, has_unsafe_intent

DemoQuery = QueryCandidate


def generate_demo_sql(question: str) -> DemoQuery | None:
    candidate = DemoQueryProvider().generate_query(question)
    return candidate if candidate.sql is not None else None
