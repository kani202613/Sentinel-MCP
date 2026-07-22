import os
import logging
from typing import Dict, Any
from .base import MCPTool

logger = logging.getLogger(__name__)

class FilesystemTool(MCPTool):
    """Tool for reading, writing, and deleting files in the simulated filesystem."""
    
    def __init__(self):
        self.base_dir = r"c:\Users\kanis\OneDrive\Desktop\SentinelMCP\data\enterprise\filesystem"
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        action = args.get("action", "").upper()
        path = args.get("path", "")
        
        if not action or action not in ["READ", "WRITE", "DELETE"]:
            return {"status": "error", "message": "Invalid or missing action."}
        if not path:
            return {"status": "error", "message": "path is required."}
            
        full_path = os.path.join(self.base_dir, path)
        
        # Prevent directory traversal outside base_dir
        if not os.path.normpath(full_path).startswith(self.base_dir):
            return {"status": "error", "message": "Invalid path."}
            
        try:
            if action == "READ":
                if not os.path.exists(full_path) or not os.path.isfile(full_path):
                    return {"status": "error", "message": "File does not exist."}
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return {"status": "success", "content": content}
                
            elif action == "WRITE":
                content = args.get("content", "")
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"status": "success", "message": "File written successfully."}
                
            elif action == "DELETE":
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    os.remove(full_path)
                    return {"status": "success", "message": "File deleted."}
                else:
                    return {"status": "error", "message": "File does not exist."}
                    
        except Exception as e:
            logger.error(f"Filesystem error: {e}")
            return {"status": "error", "message": str(e)}

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "filesystem_tool",
            "description": "Interact with the enterprise filesystem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["READ", "WRITE", "DELETE"],
                        "description": "Operation to perform on the filesystem."
                    },
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file."
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (for WRITE action)."
                    }
                },
                "required": ["action", "path"]
            }
        }
