from app.database.connection import DatabaseConnection


class SQLExecutor:

    @staticmethod
    def execute(database, query):
        connection = (
            database
            if isinstance(database, DatabaseConnection)
            else DatabaseConnection.from_sqlite_path(database)
        )
        return connection.execute_read_only(query)
