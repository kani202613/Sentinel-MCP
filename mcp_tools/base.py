from abc import ABC, abstractmethod
from typing import Dict, Any

class MCPTool(ABC):
    """Abstract base class for all MCP tools."""
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the given arguments.
        
        Args:
            args (Dict[str, Any]): Arguments for the tool.
            
        Returns:
            Dict[str, Any]: The tool execution result.
        """
        pass
        
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema definition for the tool.
        
        Returns:
            Dict[str, Any]: Tool schema definition.
        """
        pass
