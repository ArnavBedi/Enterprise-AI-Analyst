from app.services.gemini_client import GeminiClient
from app.database.connection import DatabaseConnection


class SQLService:

    def __init__(self):
        self.gemini = GeminiClient()

    def generate_sql(self, database, question):
        connection = (
            database
            if isinstance(database, DatabaseConnection)
            else DatabaseConnection.from_sqlite_path(database)
        )
        schema = connection.schema()

        prompt = f"""
You are an expert SQL analyst.

Database schema:

{schema}

User question:

{question}

Return ONLY one read-only {connection.dialect} SELECT query.

Use only tables and columns listed in the schema. Qualify table names with
their schema when one is shown. Never generate INSERT, UPDATE, DELETE, DDL,
transaction control, locking clauses, stored procedure calls, or file access.

Do not explain anything.

Do not use markdown.
"""

        sql = self.gemini.generate(prompt)

        sql = (
            sql.replace("```sql", "")
               .replace("```", "")
               .strip()
        )

        return sql
