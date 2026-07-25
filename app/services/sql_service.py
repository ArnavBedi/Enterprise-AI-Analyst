from app.services.gemini_client import GeminiClient
import sqlite3


class SQLService:

    def __init__(self):
        self.gemini = GeminiClient()

    def generate_sql(self, database_path, question):

        connection = sqlite3.connect(database_path)

        cursor = connection.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )

        tables = cursor.fetchall()

        schema = ""

        for table in tables:

            table_name = table[0]

            cursor.execute(
                f"PRAGMA table_info({table_name})"
            )

            columns = cursor.fetchall()

            schema += f"\nTable: {table_name}\n"

            for column in columns:

                schema += (
                    f"{column[1]} ({column[2]})\n"
                )

        connection.close()

        prompt = f"""
You are an expert SQL analyst.

Database schema:

{schema}

User question:

{question}

Return ONLY SQLite SQL.

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