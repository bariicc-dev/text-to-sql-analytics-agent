from app.core.config import get_settings
from app.providers.base import QueryProvider
from app.providers.demo_provider import DemoQueryProvider


class UnknownQueryProviderError(ValueError):
    pass


def get_query_provider(provider_name: str | None = None) -> QueryProvider:
    selected_provider = provider_name or get_settings().query_provider

    if selected_provider == "demo":
        return DemoQueryProvider()

    raise UnknownQueryProviderError(f"Unknown query provider: {selected_provider}")
