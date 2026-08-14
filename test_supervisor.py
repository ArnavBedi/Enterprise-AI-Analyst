from app.agents.supervisor import Supervisor

supervisor = Supervisor()

questions = [
    "Summarize this dataset.",
    "Calculate the average salary.",
    "Plot salary vs age.",
    "Show SQL for average salary by department."
]

for q in questions:

    print(q)

    print("→", supervisor.route(q))

    print()