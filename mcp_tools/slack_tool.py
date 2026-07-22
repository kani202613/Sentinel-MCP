import os
import json
import logging
from typing import Dict, Any
from .base import MCPTool

logger = logging.getLogger(__name__)

class SlackTool(MCPTool):
    """Tool for simulating Slack communications."""
    
    def __init__(self):
        self.slack_db_path = r"c:\Users\kanis\OneDrive\Desktop\SentinelMCP\data\enterprise\slack_seed.json"
        
    def _read_data(self) -> Dict[str, Any]:
        if not os.path.exists(self.slack_db_path):
            return {"channels": {}}
        with open(self.slack_db_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"channels": {}}
                
    def _write_data(self, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.slack_db_path), exist_ok=True)
        with open(self.slack_db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        action = args.get("action", "").upper()
        channel = args.get("channel")
        message = args.get("message")
        
        if not action or action not in ["READ_MESSAGES", "SEND_MESSAGE"]:
            return {"status": "error", "message": "Invalid or missing action."}
        if not channel:
            return {"status": "error", "message": "channel is required."}
            
        data = self._read_data()
        channels = data.setdefault("channels", {})
        
        try:
            if action == "READ_MESSAGES":
                messages = channels.get(channel, [])
                return {"status": "success", "channel": channel, "messages": messages}
                
            elif action == "SEND_MESSAGE":
                if not message:
                    return {"status": "error", "message": "message content is required."}
                
                channel_msgs = channels.setdefault(channel, [])
                new_msg = {
                    "id": len(channel_msgs) + 1,
                    "text": message,
                    "sender": "MCP_Bot"
                }
                channel_msgs.append(new_msg)
                self._write_data(data)
                
                return {"status": "success", "message": "Message sent.", "data": new_msg}
                
        except Exception as e:
            logger.error(f"Slack tool error: {e}")
            return {"status": "error", "message": str(e)}

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "slack_tool",
            "description": "Simulated Slack communications.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["READ_MESSAGES", "SEND_MESSAGE"],
                        "description": "Slack operation."
                    },
                    "channel": {
                        "type": "string",
                        "description": "Slack channel name (without #)."
                    },
                    "message": {
                        "type": "string",
                        "description": "Message content to send."
                    }
                },
                "required": ["action", "channel"]
            }
        }
