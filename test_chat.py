from services.chat_service import ChatService

report = {
    "rows": 5,
    "columns": 4,
    "column_names": [
        "Name",
        "Age",
        "Salary",
        "Department"
    ],
    "missing_values": {
        "Name": 0,
        "Age": 0,
        "Salary": 0,
        "Department": 0
    },
    "duplicate_rows": 0,
    "categorical_summary": {
        "Department": {
            "Engineering": 2,
            "Marketing": 2,
            "Finance": 1
        }
    }
}

chat = ChatService()

response = chat.ask(
    report,
    "Which department has the most employees?"
)

print(response)