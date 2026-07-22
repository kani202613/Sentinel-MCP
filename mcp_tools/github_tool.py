import os
import json
import logging
from typing import Dict, Any
from .base import MCPTool

logger = logging.getLogger(__name__)

class GitHubTool(MCPTool):
    """Tool for interacting with a simulated GitHub enterprise instance."""
    
    def __init__(self):
        self.github_db_path = r"c:\Users\kanis\OneDrive\Desktop\SentinelMCP\data\enterprise\github_seed.json"
        
    def _read_data(self) -> Dict[str, Any]:
        if not os.path.exists(self.github_db_path):
            return {"repositories": {}}
        with open(self.github_db_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"repositories": {}}
                
    def _write_data(self, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.github_db_path), exist_ok=True)
        with open(self.github_db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        action = args.get("action", "").upper()
        repo_name = args.get("repo_name")
        issue_id = args.get("issue_id")
        
        if not action or action not in ["LIST_REPOS", "GET_ISSUE", "CREATE_PR", "DELETE_REPO"]:
            return {"status": "error", "message": "Invalid or missing action."}
            
        data = self._read_data()
        repos = data.setdefault("repositories", {})
        
        try:
            if action == "LIST_REPOS":
                return {"status": "success", "repositories": list(repos.keys())}
                
            elif action == "GET_ISSUE":
                if not repo_name or not issue_id:
                    return {"status": "error", "message": "repo_name and issue_id required."}
                repo = repos.get(repo_name)
                if not repo:
                    return {"status": "error", "message": f"Repository '{repo_name}' not found."}
                
                # Assume issues are in repo["issues"] as a list or dict
                issues = repo.get("issues", [])
                issue = next((i for i in issues if str(i.get("id")) == str(issue_id)), None)
                if issue:
                    return {"status": "success", "issue": issue}
                return {"status": "error", "message": "Issue not found."}
                
            elif action == "CREATE_PR":
                if not repo_name:
                    return {"status": "error", "message": "repo_name required."}
                if repo_name not in repos:
                    repos[repo_name] = {"issues": [], "prs": []}
                
                prs = repos[repo_name].setdefault("prs", [])
                new_pr = {
                    "id": len(prs) + 1,
                    "title": args.get("title", "New PR"),
                    "description": args.get("description", "")
                }
                prs.append(new_pr)
                self._write_data(data)
                return {"status": "success", "message": "PR created.", "pr": new_pr}
                
            elif action == "DELETE_REPO":
                if not repo_name:
                    return {"status": "error", "message": "repo_name required."}
                if repo_name in repos:
                    del repos[repo_name]
                    self._write_data(data)
                    return {"status": "success", "message": f"Repository '{repo_name}' deleted."}
                return {"status": "error", "message": "Repository not found."}
                
        except Exception as e:
            logger.error(f"GitHub tool error: {e}")
            return {"status": "error", "message": str(e)}

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "github_tool",
            "description": "Simulated GitHub operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["LIST_REPOS", "GET_ISSUE", "CREATE_PR", "DELETE_REPO"],
                        "description": "GitHub action to perform."
                    },
                    "repo_name": {
                        "type": "string",
                        "description": "Name of the repository."
                    },
                    "issue_id": {
                        "type": "string",
                        "description": "ID of the issue to retrieve."
                    },
                    "title": {
                        "type": "string",
                        "description": "Title for a new PR."
                    },
                    "description": {
                        "type": "string",
                        "description": "Description for a new PR."
                    }
                },
                "required": ["action"]
            }
        }
