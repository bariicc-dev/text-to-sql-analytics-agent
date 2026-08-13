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
    "LOCK",
}

_ALLOWED_PREFIXES = ("SELECT", "WITH")
_COMMENT_PATTERNS = ("--", "/*", "*/")
_BLOCKED_RELATIONS = ("query_logs", "feedback", "pg_catalog", "information_schema")
_BLOCKED_FUNCTIONS = (
    "dblink",
    "lo_export",
    "lo_import",
    "pg_cancel_backend",
    "pg_ls_dir",
    "pg_read_binary_file",
    "pg_read_file",
    "pg_stat_file",
    "pg_terminate_backend",
    "set_config",
)
_LIMIT_PATTERN = re.compile(r"\bLIMIT\s+\d+\b", re.IGNORECASE)
_SELECT_STAR_PATTERN = re.compile(r"\bSELECT\s+\*", re.IGNORECASE)
_SELECT_INTO_PATTERN = re.compile(r"\bSELECT\b.+\bINTO\b", re.IGNORECASE)
_LOCKING_CLAUSE_PATTERN = re.compile(
    r"\bFOR\s+(?:UPDATE|NO\s+KEY\s+UPDATE|SHARE|KEY\s+SHARE)\b",
    re.IGNORECASE,
)
_EXTRACT_PATTERN = re.compile(r"\bEXTRACT\s*\([^)]*\)", re.IGNORECASE)
_TABLE_REFERENCE_PATTERN = re.compile(
    r'\b(?:FROM|JOIN)\s+((?:"?[A-Za-z_][\w$]*"?\.)?"?[A-Za-z_][\w$]*"?)',
    re.IGNORECASE,
)
_WORD_PATTERN = re.compile(r"\b[A-Z_]+\b")


def normalize_sql(sql: str) -> str:
    return " ".join(sql.strip().split())


def _strip_trailing_semicolon(sql: str) -> str:
    return sql[:-1].strip() if sql.endswith(";") else sql


def _blocked_keywords(normalized_sql: str) -> list[str]:
    words = set(_WORD_PATTERN.findall(normalized_sql.upper()))
    return sorted(words.intersection(BLOCKED_KEYWORDS))


def _contains_identifier(sql: str, identifier: str) -> bool:
    pattern = rf'(?<![\w$])"?{re.escape(identifier)}"?(?![\w$])'
    return re.search(pattern, sql, re.IGNORECASE) is not None


def _blocked_relation(sql: str) -> str | None:
    return next(
        (name for name in _BLOCKED_RELATIONS if _contains_identifier(sql, name)),
        None,
    )


def _blocked_function(sql: str) -> str | None:
    for name in _BLOCKED_FUNCTIONS:
        if re.search(rf'(?<![\w$])"?{re.escape(name)}"?\s*\(', sql, re.IGNORECASE):
            return name
    return None


def _uses_unapproved_schema(sql: str) -> bool:
    sql_without_extract = _EXTRACT_PATTERN.sub("", sql)
    for reference in _TABLE_REFERENCE_PATTERN.findall(sql_without_extract):
        parts = [part.strip('"').lower() for part in reference.split(".")]
        if len(parts) == 2 and parts[0] != "public":
            return True
    return False


def _unsafe_response(sql: str, reason: str, blocked_keywords: list[str] | None = None) -> SqlValidationResponse:
    return SqlValidationResponse(
        is_safe=False,
        reason=reason,
        normalized_sql=sql,
        blocked_keywords=blocked_keywords or [],
    )


def validate_sql(sql: str) -> SqlValidationResponse:
    normalized_sql = normalize_sql(sql)

    if not normalized_sql:
        return _unsafe_response("", "SQL query is empty.")

    if any(pattern in normalized_sql for pattern in _COMMENT_PATTERNS):
        return _unsafe_response(
            normalized_sql,
            "SQL comments are not allowed in submitted queries.",
        )

    body = _strip_trailing_semicolon(normalized_sql)
    if ";" in body:
        return _unsafe_response(
            normalized_sql,
            "Multiple SQL statements are not allowed.",
        )

    keyword_matches = _blocked_keywords(body)
    if keyword_matches:
        return _unsafe_response(
            normalized_sql,
            f"This query was blocked because {keyword_matches[0]} statements are not allowed.",
            keyword_matches,
        )

    if not body.upper().startswith(_ALLOWED_PREFIXES):
        return _unsafe_response(normalized_sql, "Only SELECT and WITH queries are allowed.")

    if _SELECT_INTO_PATTERN.search(body):
        return _unsafe_response(normalized_sql, "SELECT INTO is not allowed.")

    if _LOCKING_CLAUSE_PATTERN.search(body):
        return _unsafe_response(normalized_sql, "Row-locking clauses are not allowed.")

    relation = _blocked_relation(body)
    if relation is not None:
        return _unsafe_response(
            normalized_sql,
            f"Generated queries cannot access {relation}.",
        )

    if _uses_unapproved_schema(body):
        return _unsafe_response(
            normalized_sql,
            "Generated queries can use only the public analytics schema.",
        )

    function = _blocked_function(body)
    if function is not None:
        return _unsafe_response(
            normalized_sql,
            f"Generated queries cannot call {function}.",
        )

    if _SELECT_STAR_PATTERN.search(body) and not _LIMIT_PATTERN.search(body):
        return _unsafe_response(
            normalized_sql,
            "SELECT * queries must include a reasonable LIMIT.",
        )

    return SqlValidationResponse(
        is_safe=True,
        reason="Query is read-only and passed the current safety checks.",
        normalized_sql=body,
        blocked_keywords=[],
    )
