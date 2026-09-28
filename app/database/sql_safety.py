import re

from app.database.connection import DatabaseError


_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|UPSERT|CREATE|ALTER|DROP|TRUNCATE|"
    r"REPLACE|GRANT|REVOKE|COPY|CALL|EXECUTE|VACUUM|ANALYZE|ATTACH|DETACH|"
    r"PRAGMA|SET|RESET|LOCK|UNLOCK|INTO\s+OUTFILE|FOR\s+UPDATE|"
    r"FOR\s+SHARE)\b",
    re.IGNORECASE,
)

_DANGEROUS_FUNCTIONS = re.compile(
    r"\b(pg_sleep|pg_read_file|pg_read_binary_file|pg_ls_dir|"
    r"lo_import|lo_export|dblink|load_file|sleep|benchmark)\s*\(",
    re.IGNORECASE,
)


def validate_read_only_sql(query: str) -> str:
    """Allow one SELECT/CTE statement and reject mutation or locking syntax."""
    normalized = query.strip()
    if not normalized:
        raise DatabaseError("The generated SQL query was empty.")
    if len(normalized) > 50000:
        raise DatabaseError("The generated SQL query is too large.")

    without_comments = re.sub(r"/\*.*?\*/", " ", normalized, flags=re.DOTALL)
    without_comments = re.sub(r"--[^\n]*", " ", without_comments).strip()
    statements = [part.strip() for part in without_comments.split(";") if part.strip()]

    if len(statements) != 1:
        raise DatabaseError("Only one read-only SQL statement is allowed.")
    statement = statements[0]
    if not re.match(r"^(SELECT|WITH)\b", statement, flags=re.IGNORECASE):
        raise DatabaseError("Only SELECT queries and read-only CTEs are allowed.")
    if _FORBIDDEN.search(statement):
        raise DatabaseError("The query contains a prohibited SQL operation.")
    if _DANGEROUS_FUNCTIONS.search(statement):
        raise DatabaseError("The query contains a prohibited database function.")

    return statement
