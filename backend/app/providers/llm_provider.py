import json
from json import JSONDecodeError
from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.prompting.builder import build_sql_prompt
from app.providers.base import QueryCandidate

_NOT_CONFIGURED_MESSAGE = (
    "LLM provider is not configured yet. Set LLM_PROVIDER=nvidia, LLM_MODEL, "
    "LLM_API_BASE_URL, and LLM_API_KEY, or use QUERY_PROVIDER=demo."
)
_SYSTEM_MESSAGE = "Generate one safe read-only SQL candidate for the provided analytics question."


class LLMQueryProvider:
    source = "llm"

    def __init__(self, settings: Settings | None = None, client: httpx.Client | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = client

    def build_prompt_context(self, question: str) -> str:
        return build_sql_prompt(question)

    def build_request_payload(self, question: str) -> dict[str, Any]:
        return {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": _SYSTEM_MESSAGE},
                {"role": "user", "content": self.build_prompt_context(question)},
            ],
            "temperature": 0,
        }

    def generate_query(self, question: str, schema_context: Any | None = None) -> QueryCandidate:
        if (self.settings.llm_provider or "").lower().strip() != "nvidia":
            return self._not_generated(_NOT_CONFIGURED_MESSAGE)

        missing_config = self._missing_config()
        if missing_config:
            return self._not_generated(f"LLM provider is not configured yet. Missing: {', '.join(missing_config)}.")

        try:
            response_data = self._post_chat_completion(self.build_request_payload(question))
            message_content = self._extract_message_content(response_data)
        except httpx.HTTPError:
            return self._not_generated("LLM provider request failed.")
        except ValueError as exc:
            return self._not_generated(str(exc))

        return self._parse_model_response(message_content)

    def _missing_config(self) -> list[str]:
        required_config = {
            "LLM_MODEL": self.settings.llm_model,
            "LLM_API_BASE_URL": self.settings.llm_api_base_url,
            "LLM_API_KEY": self.settings.llm_api_key,
        }
        return [name for name, value in required_config.items() if not value]

    def _post_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }

        if self.client is not None:
            response = self.client.post(self._chat_completions_url(), headers=headers, json=payload)
        else:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self._chat_completions_url(), headers=headers, json=payload)

        response.raise_for_status()
        try:
            response_data = response.json()
        except ValueError as exc:
            raise ValueError("LLM provider response was not valid JSON.") from exc

        if not isinstance(response_data, dict):
            raise ValueError("LLM provider response was not a JSON object.")
        return response_data

    def _chat_completions_url(self) -> str:
        base_url = (self.settings.llm_api_base_url or "").rstrip("/")
        if base_url.endswith("/chat/completions"):
            return base_url
        return f"{base_url}/chat/completions"

    def _extract_message_content(self, response_data: dict[str, Any]) -> str:
        try:
            content = response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("LLM provider response did not include message content.") from exc

        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM provider response did not include message content.")
        return content

    def _parse_model_response(self, content: str) -> QueryCandidate:
        try:
            parsed_response = json.loads(content)
        except JSONDecodeError:
            return self._not_generated("LLM response was not valid JSON.")

        if not isinstance(parsed_response, dict):
            return self._not_generated("LLM response was not a JSON object.")

        sql = parsed_response.get("sql")
        if not isinstance(sql, str) or not sql.strip():
            return self._not_generated("LLM response did not include SQL.")

        category = parsed_response.get("category")
        reason = parsed_response.get("reason")

        return QueryCandidate(
            category=category.strip() if isinstance(category, str) and category.strip() else "llm_generated",
            sql=sql.strip(),
            source=self.source,
            confidence=0.5,
            reason=reason.strip() if isinstance(reason, str) and reason.strip() else None,
            safety_status="not_checked",
        )

    def _not_generated(self, reason: str) -> QueryCandidate:
        return QueryCandidate(
            category="unsupported",
            sql=None,
            source=self.source,
            confidence=0.0,
            reason=reason,
            safety_status="not_generated",
        )
