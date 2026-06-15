from typing import Any


def explain_result(question: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "The query ran safely, but it did not return any rows."

    return f"The demo query returned {len(rows)} row(s) for: {question}"
