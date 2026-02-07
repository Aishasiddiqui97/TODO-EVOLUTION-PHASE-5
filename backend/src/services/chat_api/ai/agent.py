"""
OpenRouter API integration for natural language task management.

Handles AI agent initialization, message processing, and tool execution.
Uses OpenRouter for access to multiple LLM models through OpenAI-compatible API.
"""

import logging
import os
from typing import Dict, Any, List, Optional
import openai

logger = logging.getLogger(__name__)


class AIAgent:
    """AI agent for natural language task management using OpenRouter."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI agent.

        Args:
            api_key: OpenRouter API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided")

        # Configure OpenAI client to use OpenRouter
        openai.api_key = self.api_key
        openai.api_base = "https://openrouter.ai/api/v1"
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo-preview")

        # System prompt for task management
        self.system_prompt = """You are a helpful task management assistant.
You help users create, update, complete, delete, and search tasks using natural language.

Available tools:
- create_task: Create a new task with title, description, priority, due date, tags, and recurrence
- update_task: Update an existing task
- complete_task: Mark a task as completed
- delete_task: Delete a task
- list_tasks: List tasks with optional filters
- search_tasks: Search tasks using natural language queries
- get_preferences: Get user preferences
- update_preferences: Update user preferences

When users ask about tasks, use the appropriate tool to help them.
Be conversational and helpful. Confirm actions after completing them.
"""

    async def process_message(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        available_tools: List[Dict[str, Any]],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        Args:
            message: User message
            conversation_history: Previous conversation messages
            available_tools: List of available MCP tools
            user_id: User ID for context

        Returns:
            Response with message and tool calls
        """
        try:
            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]

            # Add conversation history
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })

            # Call OpenAI with function calling
            response = await self._call_openai(messages, available_tools)

            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "response": "I'm sorry, I encountered an error processing your request. Please try again.",
                "tool_calls": [],
                "error": str(e)
            }

    async def _call_openai(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Call OpenRouter API with function calling.

        Args:
            messages: Conversation messages
            tools: Available tools

        Returns:
            Response with message and tool calls
        """
        try:
            # Convert MCP tools to OpenAI function format
            functions = self._convert_tools_to_functions(tools)

            # Call OpenRouter (OpenAI-compatible API)
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                functions=functions if functions else None,
                function_call="auto" if functions else None,
                temperature=0.7,
                max_tokens=1000
            )

            # Extract response
            message = response.choices[0].message

            result = {
                "response": message.get("content", ""),
                "tool_calls": []
            }

            # Extract function calls if any
            if message.get("function_call"):
                import json
                func_call = message["function_call"]
                result["tool_calls"].append({
                    "tool": func_call["name"],
                    "arguments": json.loads(func_call["arguments"])
                })

            return result

        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}", exc_info=True)
            raise

    def _convert_tools_to_functions(
        self,
        tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert MCP tools to OpenAI function format.

        Args:
            tools: MCP tools

        Returns:
            OpenAI function definitions
        """
        functions = []

        for tool in tools:
            function = {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": {
                    "type": "object",
                    "properties": tool.get("parameters", {}),
                    "required": tool.get("required", [])
                }
            }
            functions.append(function)

        return functions

    async def execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        mcp_tools: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool call.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            mcp_tools: Available MCP tools

        Returns:
            Tool execution result
        """
        try:
            if tool_name not in mcp_tools:
                return {
                    "success": False,
                    "error": f"Tool not found: {tool_name}"
                }

            # Execute the tool
            tool = mcp_tools[tool_name]
            result = await tool(**arguments)

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

    def generate_response_from_tool_results(
        self,
        tool_calls: List[Dict[str, Any]],
        tool_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a natural language response from tool results.

        Args:
            tool_calls: List of tool calls made
            tool_results: List of tool results

        Returns:
            Natural language response
        """
        try:
            # Simple response generation based on tool results
            responses = []

            for tool_call, result in zip(tool_calls, tool_results):
                tool_name = tool_call["tool"]

                if not result.get("success"):
                    responses.append(f"I encountered an error: {result.get('error', 'Unknown error')}")
                    continue

                # Generate response based on tool type
                if tool_name == "create_task":
                    task = result["result"]
                    responses.append(f"I've created the task '{task['title']}' with {task['priority']} priority.")

                elif tool_name == "update_task":
                    task = result["result"]
                    responses.append(f"I've updated the task '{task['title']}'.")

                elif tool_name == "complete_task":
                    task = result["result"]
                    responses.append(f"Great! I've marked '{task['title']}' as completed.")

                elif tool_name == "delete_task":
                    responses.append("I've deleted the task.")

                elif tool_name == "list_tasks":
                    tasks = result["result"]
                    if not tasks:
                        responses.append("You don't have any tasks matching those criteria.")
                    else:
                        responses.append(f"I found {len(tasks)} task(s):")
                        for task in tasks[:5]:  # Show first 5
                            responses.append(f"- {task['title']} ({task['priority']} priority, {task['status']})")

                elif tool_name == "search_tasks":
                    tasks = result["result"]
                    if not tasks:
                        responses.append("I couldn't find any tasks matching your search.")
                    else:
                        responses.append(f"I found {len(tasks)} task(s) matching your search:")
                        for task in tasks[:5]:
                            responses.append(f"- {task['title']} ({task['priority']} priority)")

            return "\n".join(responses) if responses else "Done!"

        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return "I completed the action, but had trouble generating a response."
