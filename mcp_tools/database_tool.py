from typing import Dict, Any
from .base import MCPTool

class DatabaseTool(MCPTool):
    """Tool for simulating SQL query execution against HR/Financial databases."""
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        query = args.get("query", "")
        # Simulate returning dummy data based on keywords
        results = []
        if "employees" in query.lower() or "hr" in query.lower():
            results = [{"id": 1, "name": "Alice", "department": "HR"}, {"id": 2, "name": "Bob", "department": "Engineering"}]
        elif "finance" in query.lower() or "salary" in query.lower():
            results = [{"id": 1, "salary": 120000}, {"id": 2, "salary": 95000}]
        else:
            results = [{"col1": "val1", "col2": "val2"}]
            
        return {
            "status": "success",
            "query_executed": query,
            "row_count": len(results),
            "results": results
        }

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "database_query",
            "description": "Execute SQL queries against HR/Financial databases.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query string to execute."
                    }
                },
                "required": ["query"]
            }
        }
