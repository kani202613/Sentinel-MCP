import os
import json
import logging
from typing import Dict, Any
from .base import MCPTool

logger = logging.getLogger(__name__)

class DatabaseTool(MCPTool):
    """Tool for interacting with a simulated database."""
    
    def __init__(self):
        self.db_path = r"c:\Users\kanis\OneDrive\Desktop\SentinelMCP\data\enterprise\database_seed.json"
        
    def _read_db(self) -> Dict[str, Any]:
        if not os.path.exists(self.db_path):
            return {}
        with open(self.db_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
                
    def _write_db(self, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        action = args.get("action", "").upper()
        table_name = args.get("table_name")
        query = args.get("query", {})
        
        if not action or action not in ["SELECT", "UPDATE", "DELETE", "INSERT"]:
            return {"status": "error", "message": "Invalid or missing action."}
        if not table_name:
            return {"status": "error", "message": "table_name is required."}
            
        db_data = self._read_db()
        if table_name not in db_data and action != "INSERT":
            return {"status": "error", "message": f"Table '{table_name}' does not exist."}
            
        try:
            if action == "SELECT":
                table = db_data.get(table_name, [])
                # Simple filter based on query dict if provided
                results = table
                if query and isinstance(query, dict):
                    results = [row for row in table if all(row.get(k) == v for k, v in query.items())]
                return {"status": "success", "results": results}
                
            elif action == "INSERT":
                if table_name not in db_data:
                    db_data[table_name] = []
                data_to_insert = args.get("data", {})
                db_data[table_name].append(data_to_insert)
                self._write_db(db_data)
                return {"status": "success", "message": "Record inserted."}
                
            elif action == "UPDATE":
                table = db_data.get(table_name, [])
                update_data = args.get("data", {})
                count = 0
                for row in table:
                    if not query or all(row.get(k) == v for k, v in query.items()):
                        row.update(update_data)
                        count += 1
                self._write_db(db_data)
                return {"status": "success", "message": f"Updated {count} records."}
                
            elif action == "DELETE":
                table = db_data.get(table_name, [])
                if not query:
                    # DELETE ALL if no query
                    db_data[table_name] = []
                    count = len(table)
                else:
                    new_table = [row for row in table if not all(row.get(k) == v for k, v in query.items())]
                    count = len(table) - len(new_table)
                    db_data[table_name] = new_table
                self._write_db(db_data)
                return {"status": "success", "message": f"Deleted {count} records."}
                
        except Exception as e:
            logger.error(f"Database error: {e}")
            return {"status": "error", "message": str(e)}

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "database_tool",
            "description": "Interact with simulated JSON database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["SELECT", "UPDATE", "DELETE", "INSERT"],
                        "description": "Database operation to perform."
                    },
                    "table_name": {
                        "type": "string",
                        "description": "Table to operate on."
                    },
                    "query": {
                        "type": "object",
                        "description": "Key-value pairs for filtering (WHERE clause equivalent)."
                    },
                    "data": {
                        "type": "object",
                        "description": "Data payload for INSERT or UPDATE."
                    }
                },
                "required": ["action", "table_name"]
            }
        }
