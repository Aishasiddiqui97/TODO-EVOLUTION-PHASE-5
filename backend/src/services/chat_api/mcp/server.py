"""
MCP server integration for exposing tools to the AI agent.

Provides a registry of MCP tools and their metadata for function calling.
"""

import logging
from typing import Dict, Any, List, Callable
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from mcp.tools.create_task import create_task
from mcp.tools.update_task import update_task
from mcp.tools.complete_task import complete_task
from mcp.tools.delete_task import delete_task
from mcp.tools.list_tasks import list_tasks
from mcp.tools.search_tasks import search_tasks

logger = logging.getLogger(__name__)


class MCPServer:
    """MCP server for managing and exposing tools."""

    def __init__(self, task_service, conversation_service):
        """
        Initialize MCP server.

        Args:
            task_service: Task service instance
            conversation_service: Conversation service instance
        """
        self.task_service = task_service
        self.conversation_service = conversation_service
        self.tools = {}
        self._register_tools()

    def _register_tools(self):
        """Register all available MCP tools."""

        # Create task tool
        self.tools["create_task"] = {
            "name": "create_task",
            "description": "Create a new task with title, description, priority, due date, tags, and optional recurrence pattern",
            "function": self._wrap_create_task,
            "parameters": {
                "title": {
                    "type": "string",
                    "description": "Task title"
                },
                "description": {
                    "type": "string",
                    "description": "Task description (optional)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Task priority (default: medium)"
                },
                "dueDate": {
                    "type": "string",
                    "description": "Due date in ISO format YYYY-MM-DD (optional)"
                },
                "dueTime": {
                    "type": "string",
                    "description": "Due time in HH:MM format (optional)"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tags (optional)"
                },
                "recurrencePattern": {
                    "type": "string",
                    "description": "Recurrence pattern like 'every day', 'every Monday' (optional)"
                }
            },
            "required": ["title"]
        }

        # Update task tool
        self.tools["update_task"] = {
            "name": "update_task",
            "description": "Update an existing task's properties",
            "function": self._wrap_update_task,
            "parameters": {
                "taskId": {
                    "type": "string",
                    "description": "Task ID to update"
                },
                "title": {
                    "type": "string",
                    "description": "New title (optional)"
                },
                "description": {
                    "type": "string",
                    "description": "New description (optional)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "New priority (optional)"
                },
                "dueDate": {
                    "type": "string",
                    "description": "New due date (optional)"
                },
                "dueTime": {
                    "type": "string",
                    "description": "New due time (optional)"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New tags (optional)"
                }
            },
            "required": ["taskId"]
        }

        # Complete task tool
        self.tools["complete_task"] = {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "function": self._wrap_complete_task,
            "parameters": {
                "taskId": {
                    "type": "string",
                    "description": "Task ID to complete"
                }
            },
            "required": ["taskId"]
        }

        # Delete task tool
        self.tools["delete_task"] = {
            "name": "delete_task",
            "description": "Delete a task",
            "function": self._wrap_delete_task,
            "parameters": {
                "taskId": {
                    "type": "string",
                    "description": "Task ID to delete"
                }
            },
            "required": ["taskId"]
        }

        # List tasks tool
        self.tools["list_tasks"] = {
            "name": "list_tasks",
            "description": "List tasks with optional filters for status, priority, and tags",
            "function": self._wrap_list_tasks,
            "parameters": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed"],
                    "description": "Filter by status (optional)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Filter by priority (optional)"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by tags (optional)"
                }
            },
            "required": []
        }

        # Search tasks tool
        self.tools["search_tasks"] = {
            "name": "search_tasks",
            "description": "Search tasks using natural language query",
            "function": self._wrap_search_tasks,
            "parameters": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query"
                }
            },
            "required": ["query"]
        }

        logger.info(f"Registered {len(self.tools)} MCP tools")

    async def _wrap_create_task(self, userId: str, **kwargs):
        """Wrapper for create_task tool."""
        return await self.task_service.create_task(user_id=userId, **kwargs)

    async def _wrap_update_task(self, taskId: str, **kwargs):
        """Wrapper for update_task tool."""
        return await self.task_service.update_task(task_id=taskId, updates=kwargs)

    async def _wrap_complete_task(self, taskId: str):
        """Wrapper for complete_task tool."""
        return await self.task_service.complete_task(task_id=taskId)

    async def _wrap_delete_task(self, taskId: str):
        """Wrapper for delete_task tool."""
        result = await self.task_service.delete_task(task_id=taskId)
        return {"success": result}

    async def _wrap_list_tasks(self, userId: str, **kwargs):
        """Wrapper for list_tasks tool."""
        return await self.task_service.list_tasks(user_id=userId, **kwargs)

    async def _wrap_search_tasks(self, userId: str, query: str):
        """Wrapper for search_tasks tool."""
        # Import search_tasks function
        from mcp.tools.search_tasks import search_tasks as search_func
        return await search_func(userId=userId, query=query)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for AI agent.

        Returns:
            List of tool definitions
        """
        definitions = []
        for tool_name, tool_info in self.tools.items():
            definitions.append({
                "name": tool_info["name"],
                "description": tool_info["description"],
                "parameters": tool_info["parameters"],
                "required": tool_info["required"]
            })
        return definitions

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            user_id: User ID for context

        Returns:
            Tool execution result
        """
        try:
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Tool not found: {tool_name}"
                }

            tool = self.tools[tool_name]

            # Add userId to arguments if not present
            if "userId" not in arguments:
                arguments["userId"] = user_id

            # Execute the tool
            result = await tool["function"](**arguments)

            return {
                "success": True,
                "result": result
            }

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_tool_function(self, tool_name: str) -> Callable:
        """
        Get tool function by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool function
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        return self.tools[tool_name]["function"]
