"""
Chat endpoint for natural language task management.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    userId: str
    conversationId: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    conversationId: str
    toolCalls: Optional[List[Dict[str, Any]]] = None


@router.post("/api/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    conversation_service=Depends(lambda: None),  # Will be injected in main.py
    ai_agent=Depends(lambda: None),  # Will be injected in main.py
    mcp_server=Depends(lambda: None)  # Will be injected in main.py
):
    """
    Process a chat message and return AI response.

    Args:
        request: Chat request with message and user ID

    Returns:
        Chat response with AI-generated message
    """
    try:
        # Get or create conversation
        if request.conversationId:
            conversation = await conversation_service.get_conversation(request.conversationId)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = await conversation_service.create_conversation(request.userId)

        conversation_id = conversation["id"]

        # Add user message to conversation
        await conversation_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        # Get conversation history
        history = await conversation_service.get_conversation_history(conversation_id)

        # Get available tools
        tool_definitions = mcp_server.get_tool_definitions()

        # Process message with AI
        ai_response = await ai_agent.process_message(
            message=request.message,
            conversation_history=history,
            available_tools=tool_definitions,
            user_id=request.userId
        )

        # Execute tool calls if any
        tool_results = []
        if ai_response.get("tool_calls"):
            for tool_call in ai_response["tool_calls"]:
                result = await mcp_server.execute_tool(
                    tool_name=tool_call["tool"],
                    arguments=tool_call["arguments"],
                    user_id=request.userId
                )
                tool_results.append(result)

            # Generate response from tool results
            response_text = ai_agent.generate_response_from_tool_results(
                tool_calls=ai_response["tool_calls"],
                tool_results=tool_results
            )
        else:
            response_text = ai_response.get("response", "I'm not sure how to help with that.")

        # Add assistant message to conversation
        await conversation_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            tool_calls=ai_response.get("tool_calls")
        )

        return ChatResponse(
            response=response_text,
            conversationId=conversation_id,
            toolCalls=ai_response.get("tool_calls")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")
