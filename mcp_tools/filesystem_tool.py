from typing import Dict, Any
from .base import MCPTool

class FilesystemTool(MCPTool):
    """Tool for simulating filesystem operations."""
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        operation = args.get("operation", "read")
        path = args.get("path", "/tmp/dummy.txt")
        
        if operation == "write":
            content = args.get("content", "")
            return {
                "status": "success",
                "operation": operation,
                "path": path,
                "bytes_written": len(content)
            }
        else:
            # Default to read
            return {
                "status": "success",
                "operation": operation,
                "path": path,
                "content": f"Simulated file content from {path}."
            }

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "filesystem",
            "description": "Read from or write to files on the filesystem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write"],
                        "description": "The filesystem operation to perform."
                    },
                    "path": {
                        "type": "string",
                        "description": "The absolute or relative file path."
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (required if operation is 'write')."
                    }
                },
                "required": ["operation", "path"]
            }
        }
