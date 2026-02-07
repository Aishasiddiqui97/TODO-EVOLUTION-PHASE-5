"""
Conversation service for managing chat conversations and state.

Handles conversation history, context management, and state persistence.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from shared.dapr_client.client import DaprClient
from shared.utils.state_keys import generate_conversation_key, generate_user_conversations_key

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing chat conversations."""

    def __init__(self, dapr_client: DaprClient):
        """
        Initialize conversation service.

        Args:
            dapr_client: Dapr client for state operations
        """
        self.dapr_client = dapr_client

    async def create_conversation(self, user_id: str) -> Dict[str, Any]:
        """
        Create a new conversation.

        Args:
            user_id: User ID

        Returns:
            Conversation data
        """
        try:
            conversation_id = f"conv-{uuid.uuid4()}"
            timestamp = datetime.utcnow().isoformat() + "Z"

            conversation_data = {
                "id": conversation_id,
                "userId": user_id,
                "messages": [],
                "createdAt": timestamp,
                "updatedAt": timestamp
            }

            # Save to state store
            conv_key = generate_conversation_key(conversation_id)
            await self.dapr_client.save_state(conv_key, conversation_data)

            # Add to user's conversation list
            await self._add_conversation_to_user_list(user_id, conversation_id)

            logger.info(f"Conversation created: {conversation_id} for user: {user_id}")
            return conversation_data

        except Exception as e:
            logger.error(f"Error creating conversation: {e}", exc_info=True)
            raise

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation by ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation data or None if not found
        """
        try:
            conv_key = generate_conversation_key(conversation_id)
            conversation = await self.dapr_client.get_state(conv_key)
            return conversation
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {e}", exc_info=True)
            return None

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role (user, assistant, system)
            content: Message content
            tool_calls: Optional tool calls made

        Returns:
            Updated conversation data or None if not found
        """
        try:
            # Get existing conversation
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                logger.warning(f"Conversation not found: {conversation_id}")
                return None

            # Create message
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            if tool_calls:
                message["toolCalls"] = tool_calls

            # Add to conversation
            conversation["messages"].append(message)
            conversation["updatedAt"] = message["timestamp"]

            # Save to state store
            conv_key = generate_conversation_key(conversation_id)
            await self.dapr_client.save_state(conv_key, conversation)

            logger.info(f"Message added to conversation: {conversation_id}")
            return conversation

        except Exception as e:
            logger.error(f"Error adding message to conversation {conversation_id}: {e}", exc_info=True)
            raise

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation message history.

        Args:
            conversation_id: Conversation ID
            limit: Optional limit on number of messages

        Returns:
            List of messages
        """
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return []

            messages = conversation.get("messages", [])
            if limit:
                messages = messages[-limit:]

            return messages

        except Exception as e:
            logger.error(f"Error getting conversation history {conversation_id}: {e}", exc_info=True)
            return []

    async def list_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all conversations for a user.

        Args:
            user_id: User ID

        Returns:
            List of conversations
        """
        try:
            # Get user's conversation list
            user_convs_key = generate_user_conversations_key(user_id)
            conversation_ids = await self.dapr_client.get_state(user_convs_key) or []

            # Fetch all conversations
            conversations = []
            for conv_id in conversation_ids:
                conv = await self.get_conversation(conv_id)
                if conv:
                    conversations.append(conv)

            return conversations

        except Exception as e:
            logger.error(f"Error listing conversations for user {user_id}: {e}", exc_info=True)
            return []

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found
        """
        try:
            # Get existing conversation
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                logger.warning(f"Conversation not found: {conversation_id}")
                return False

            user_id = conversation["userId"]

            # Delete from state store
            conv_key = generate_conversation_key(conversation_id)
            await self.dapr_client.delete_state(conv_key)

            # Remove from user's conversation list
            await self._remove_conversation_from_user_list(user_id, conversation_id)

            logger.info(f"Conversation deleted: {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {e}", exc_info=True)
            raise

    async def _add_conversation_to_user_list(self, user_id: str, conversation_id: str):
        """Add conversation ID to user's conversation list."""
        user_convs_key = generate_user_conversations_key(user_id)
        conv_ids = await self.dapr_client.get_state(user_convs_key) or []
        if conversation_id not in conv_ids:
            conv_ids.append(conversation_id)
            await self.dapr_client.save_state(user_convs_key, conv_ids)

    async def _remove_conversation_from_user_list(self, user_id: str, conversation_id: str):
        """Remove conversation ID from user's conversation list."""
        user_convs_key = generate_user_conversations_key(user_id)
        conv_ids = await self.dapr_client.get_state(user_convs_key) or []
        if conversation_id in conv_ids:
            conv_ids.remove(conversation_id)
            await self.dapr_client.save_state(user_convs_key, conv_ids)
