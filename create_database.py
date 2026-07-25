import sqlite3

connection = sqlite3.connect("data/employees.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    salary REAL,
    department TEXT
)
""")

employees = [
    (1, "Alice", 25, 70000, "Engineering"),
    (2, "Bob", 29, 85000, "Marketing"),
    (3, "Charlie", 35, 105000, "Engineering"),
    (4, "David", 31, 90000, "Finance"),
    (5, "Emma", 27, 78000, "Marketing")
]

cursor.execute("DELETE FROM employees")

cursor.executemany(
    "INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
    employees
)

connection.commit()
connection.close()

print("Database created successfully!")