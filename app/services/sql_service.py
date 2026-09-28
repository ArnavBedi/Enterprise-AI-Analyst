from app.services.gemini_client import GeminiClient
from app.database.connection import DatabaseConnection


class SQLService:

    def __init__(self):
        self.gemini = GeminiClient()

    def generate_sql(self, database, question, conversation_history=None):
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

Recent conversation context:

{(conversation_history or [])[-6:]}

Return ONLY one read-only {connection.dialect} SELECT query.

Use only tables and columns listed in the schema. Qualify table names with
their schema when one is shown. Never generate INSERT, UPDATE, DELETE, DDL,
transaction control, locking clauses, stored procedure calls, or file access.
Use the listed foreign-key relationships for joins. Never guess a relationship
that is not present in the schema. Select only columns needed for the answer.

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
