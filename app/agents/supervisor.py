from app.agents.business_agent import BusinessAgent
from app.agents.python_agent import PythonAgent
from app.agents.sql_agent import SQLAgent
from app.agents.chart_agent import ChartAgent


class Supervisor:

    def __init__(self):

        self.business = BusinessAgent()
        self.python = PythonAgent()
        self.sql = SQLAgent()
        self.chart = ChartAgent()

    def route(self, question: str):

        words = question.lower().split()

        chart_keywords = [
            "plot",
            "graph",
            "chart",
            "scatter",
            "histogram",
            "bar",
            "line",
            "boxplot"
        ]

        sql_keywords = [
            "database",
            "sql",
            "table",
            "sqlite"
        ]

        python_keywords = [
            "average",
            "sum",
            "count",
            "maximum",
            "minimum",
            "calculate",
            "correlation"
        ]

        if any(keyword in words for keyword in chart_keywords):
            return "chart"

        if any(keyword in words for keyword in sql_keywords):
            return "sql"

        if any(keyword in words for keyword in python_keywords):
            return "python"

        return "business"