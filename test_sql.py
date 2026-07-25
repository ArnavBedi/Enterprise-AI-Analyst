from app.services.sql_service import SQLService
from app.tools.sql_executor import SQLExecutor

sql_service = SQLService()

database = "data/employees.db"

question = "What is the average salary by department?"

sql = sql_service.generate_sql(
    database,
    question
)

print("Generated SQL:")
print(sql)

print("\nResult:")

result = SQLExecutor.execute(
    database,
    sql
)

print(result)