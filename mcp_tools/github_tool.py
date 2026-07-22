from typing import Dict, Any
from .base import MCPTool

class GitHubTool(MCPTool):
    """Tool for simulating GitHub interactions."""
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        action = args.get("action", "list_issues")
        repo = args.get("repo", "owner/repo")
        
        data = []
        if action == "list_issues":
            data = [{"number": 101, "title": "Fix login bug", "state": "open"}]
        elif action == "list_prs":
            data = [{"number": 202, "title": "Add OAuth support", "state": "open"}]
        elif action == "list_commits":
            data = [{"sha": "abc1234", "message": "Initial commit", "author": "dev@example.com"}]
            
        return {
            "status": "success",
            "repo": repo,
            "action": action,
            "data": data
        }

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "github",
            "description": "Interact with GitHub issues, PRs, and commits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list_issues", "list_prs", "list_commits"],
                        "description": "The GitHub action to perform."
                    },
                    "repo": {
                        "type": "string",
                        "description": "The repository in 'owner/repo' format."
                    }
                },
                "required": ["action", "repo"]
            }
        }
