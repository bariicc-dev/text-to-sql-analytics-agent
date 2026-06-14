import re

from app.models.schemas import SqlValidationResponse

BLOCKED_KEYWORDS = {
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "COPY",
    "EXEC",
    "MERGE",
    "CALL",
}

_ALLOWED_PREFIXES = ("SELECT", "WITH")
_COMMENT_PATTERNS = ("--", "/*", "*/")
_LIMIT_PATTERN = re.compile(r"\bLIMIT\s+\d+\b", re.IGNORECASE)
_SELECT_STAR_PATTERN = re.compile(r"\bSELECT\s+\*\b", re.IGNORECASE)
_WORD_PATTERN = re.compile(r"\b[A-Z_]+\b")


def normalize_sql(sql: str) -> str:
    return " ".join(sql.strip().split())


def _strip_trailing_semicolon(sql: str) -> str:
    return sql[:-1].strip() if sql.endswith(";") else sql


def _blocked_keywords(normalized_sql: str) -> list[str]:
    words = set(_WORD_PATTERN.findall(normalized_sql.upper()))
    return sorted(words.intersection(BLOCKED_KEYWORDS))


def validate_sql(sql: str) -> SqlValidationResponse:
    normalized_sql = normalize_sql(sql)

    if not normalized_sql:
        return SqlValidationResponse(
            is_safe=False,
            reason="SQL query is empty.",
            normalized_sql="",
            blocked_keywords=[],
        )

    for pattern in _COMMENT_PATTERNS:
        if pattern in normalized_sql:
            return SqlValidationResponse(
                is_safe=False,
                reason="SQL comments are not allowed in submitted queries.",
                normalized_sql=normalized_sql,
                blocked_keywords=[],
            )

    body = _strip_trailing_semicolon(normalized_sql)
    if ";" in body:
        return SqlValidationResponse(
            is_safe=False,
            reason="Multiple SQL statements are not allowed.",
            normalized_sql=normalized_sql,
            blocked_keywords=[],
        )

    keyword_matches = _blocked_keywords(body)
    if keyword_matches:
        return SqlValidationResponse(
            is_safe=False,
            reason=f"This query was blocked because {keyword_matches[0]} statements are not allowed.",
            normalized_sql=normalized_sql,
            blocked_keywords=keyword_matches,
        )

    upper_body = body.upper()
    if not upper_body.startswith(_ALLOWED_PREFIXES):
        return SqlValidationResponse(
            is_safe=False,
            reason="Only SELECT and WITH queries are allowed.",
            normalized_sql=normalized_sql,
            blocked_keywords=[],
        )

    if _SELECT_STAR_PATTERN.search(body) and not _LIMIT_PATTERN.search(body):
        return SqlValidationResponse(
            is_safe=False,
            reason="SELECT * queries must include a reasonable LIMIT.",
            normalized_sql=normalized_sql,
            blocked_keywords=[],
        )

    return SqlValidationResponse(
        is_safe=True,
        reason="Query is read-only and passed the current safety checks.",
        normalized_sql=body,
        blocked_keywords=[],
    )
