import sqlite3
import pandas as pd


class SQLExecutor:

    @staticmethod
    def execute(database_path, query):

        connection = sqlite3.connect(database_path)

        try:

            result = pd.read_sql_query(
                query,
                connection
            )

            return result

        finally:

            connection.close()