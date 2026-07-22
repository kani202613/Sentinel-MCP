import os
import json
import logging
from typing import Dict, Any
from .base import MCPTool

logger = logging.getLogger(__name__)

class PDFReaderTool(MCPTool):
    """Tool for simulating reading PDF files."""
    
    def __init__(self):
        self.base_dir = r"c:\Users\kanis\OneDrive\Desktop\SentinelMCP\data\enterprise\filesystem"
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        filepath = args.get("filepath", "")
        if not filepath:
            return {"status": "error", "message": "filepath is required."}
            
        full_path = os.path.join(self.base_dir, filepath)
        
        # Prevent directory traversal
        if not os.path.normpath(full_path).startswith(self.base_dir):
            return {"status": "error", "message": "Invalid filepath."}
            
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            return {"status": "error", "message": f"File '{filepath}' does not exist."}
            
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                
            return {
                "status": "success",
                "content": content,
                "metadata": {
                    "filename": filepath,
                    "size_bytes": os.path.getsize(full_path)
                }
            }
        except Exception as e:
            logger.error(f"Error reading PDF {filepath}: {e}")
            return {"status": "error", "message": str(e)}

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "pdf_reader",
            "description": "Read and extract text from files (simulated PDF reader).",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path or name of the file to read."
                    }
                },
                "required": ["filepath"]
            }
        }
