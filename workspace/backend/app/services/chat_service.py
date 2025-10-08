"""
Chat Service for Routix Platform
Handles conversation creation, message management, and AI-powered features
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import uuid
import re
from app.core.config import settings
from app.services.ai_service import vision_ai_service, embedding_service, AIServiceError
from app.services.redis_service import redis_service

class ConversationType(str, Enum):
    """Conversation type enumeration"""
    TEMPLATE_REQUEST = "template_request"
    GENERATION_DISCUSSION = "generation_discussion"
    SUPPORT = "support"
    GENERAL = "general"
    AI_ASSISTANT = "ai_assistant"

class MessageType(str, Enum):
    """Message type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"
    GENERATION_REQUEST = "generation_request"
    TEMPLATE_SHARE = "template_share"

class ChatServiceError(Exception):
    """Custom exception for chat service errors"""
    pass

class ChatService:
    """Complete conversation and message management service"""
    
    def __init__(self):
        # Configuration
        self.max_message_length = 10000
        self.max_messages_per_conversation = 1000
        self.conversation_cache_ttl = 86400  # 24 hours
        self.message_cache_ttl = 3600  # 1 hour
        
        # Auto-titling configuration
        self.auto_title_threshold = 3  # Messages before auto-titling
        self.title_max_length = 100
        
        # Search configuration
        self.search_limit = 50
        self.context_window = 10  # Messages for context
        
    async def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
        conversation_type: ConversationType = ConversationType.GENERAL,
        participants: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation
        
        Args:
            user_id: ID of the user creating the conversation
            title: Optional conversation title
            conversation_type: Type of conversation
            participants: List of participant user IDs
            metadata: Additional conversation metadata
            
        Returns:
            Created conversation data
        """
        try:
            print(f"[{datetime.utcnow()}] Creating conversation for user {user_id}")
            
            # Generate conversation ID
            conversation_id = self._generate_conversation_id()
            
            # Prepare participants list
            if participants is None:
                participants = [user_id]
            elif user_id not in participants:
                participants.append(user_id)
            
            # Create conversation data
            conversation_data = {
                "id": conversation_id,
                "title": title or "New Conversation",
                "type": conversation_type,
                "creator_id": user_id,
                "participants": participants,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "message_count": 0,
                "is_active": True,
                "auto_titled": False,
                "metadata": metadata or {},
                "settings": {
                    "auto_title": True,
                    "notifications": True,
                    "search_enabled": True
                }
            }
            
            # Cache conversation
            await self._cache_conversation_data(conversation_id, conversation_data)
            
            # Track conversation creation
            await self._track_conversation_event(conversation_id, "created", user_id)
            
            print(f"[{datetime.utcnow()}] Conversation created: {conversation_id}")
            
            return {
                "conversation": conversation_data,
                "message": "Conversation created successfully"
            }
            
        except Exception as e:
            print(f"Conversation creation failed: {e}")
            raise ChatServiceError(f"Failed to create conversation: {str(e)}")
    
    async def get_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        conversation_type: Optional[ConversationType] = None,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get user's conversations with filtering and pagination
        
        Args:
            user_id: User ID
            limit: Maximum results to return
            offset: Results offset for pagination
            conversation_type: Optional type filter
            search_query: Optional search query
            
        Returns:
            List of user's conversations
        """
        try:
            # Get user's conversations (mock implementation)
            conversations = await self._get_user_conversations(
                user_id, limit, offset, conversation_type, search_query
            )
            
            # Enhance conversations with recent messages
            enhanced_conversations = []
            for conv in conversations:
                # Get recent messages
                recent_messages = await self._get_recent_messages(conv["id"], 3)
                conv["recent_messages"] = recent_messages
                
                # Calculate unread count (mock)
                conv["unread_count"] = await self._get_unread_count(conv["id"], user_id)
                
                enhanced_conversations.append(conv)
            
            return {
                "conversations": enhanced_conversations,
                "pagination": {
                    "total": len(conversations),
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(conversations) == limit
                }
            }
            
        except Exception as e:
            print(f"Failed to get conversations for user {user_id}: {e}")
            raise ChatServiceError(f"Failed to get conversations: {str(e)}")
    
    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
        include_messages: bool = True,
        message_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get conversation details with messages
        
        Args:
            conversation_id: Conversation ID
            user_id: User requesting the conversation
            include_messages: Whether to include messages
            message_limit: Maximum messages to return
            
        Returns:
            Conversation data with messages
        """
        try:
            # Get conversation data
            conversation_data = await self._get_cached_conversation_data(conversation_id)
            
            if not conversation_data:
                raise ChatServiceError(f"Conversation not found: {conversation_id}")
            
            # Validate user access
            if user_id not in conversation_data.get("participants", []):
                raise ChatServiceError("Access denied to conversation")
            
            # Include messages if requested
            if include_messages:
                messages = await self._get_conversation_messages(conversation_id, message_limit)
                conversation_data["messages"] = messages
            
            # Update last read timestamp
            await self._update_last_read(conversation_id, user_id)
            
            # Track conversation access
            await self._track_conversation_event(conversation_id, "accessed", user_id)
            
            return conversation_data
            
        except Exception as e:
            print(f"Failed to get conversation {conversation_id}: {e}")
            raise ChatServiceError(f"Failed to get conversation: {str(e)}")
    
    async def send_message(
        self,
        conversation_id: str,
        user_id: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a conversation
        
        Args:
            conversation_id: Target conversation ID
            user_id: Sender user ID
            content: Message content
            message_type: Type of message
            reply_to: Optional message ID being replied to
            attachments: Optional file attachments
            metadata: Additional message metadata
            
        Returns:
            Sent message data
        """
        try:
            print(f"[{datetime.utcnow()}] Sending message to conversation {conversation_id}")
            
            # Validate conversation access
            conversation_data = await self._get_cached_conversation_data(conversation_id)
            if not conversation_data:
                raise ChatServiceError(f"Conversation not found: {conversation_id}")
            
            if user_id not in conversation_data.get("participants", []):
                raise ChatServiceError("Access denied to conversation")
            
            # Validate message content
            await self._validate_message_content(content, message_type)
            
            # Generate message ID
            message_id = self._generate_message_id()
            
            # Create message data
            message_data = {
                "id": message_id,
                "conversation_id": conversation_id,
                "sender_id": user_id,
                "content": content,
                "type": message_type,
                "reply_to": reply_to,
                "attachments": attachments or [],
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "edited": False,
                "reactions": {},
                "thread_messages": []
            }
            
            # Store message
            await self._store_message(message_data)
            
            # Update conversation
            await self._update_conversation_after_message(conversation_id, message_data)
            
            # Auto-title conversation if needed
            if conversation_data.get("settings", {}).get("auto_title", True):
                await self._maybe_auto_title_conversation(conversation_id, conversation_data)
            
            # Track message sent
            await self._track_conversation_event(conversation_id, "message_sent", user_id)
            
            print(f"[{datetime.utcnow()}] Message sent: {message_id}")
            
            return {
                "message": message_data,
                "conversation_updated": True
            }
            
        except Exception as e:
            print(f"Failed to send message: {e}")
            raise ChatServiceError(f"Failed to send message: {str(e)}")
    
    async def update_conversation_title(
        self,
        conversation_id: str,
        user_id: str,
        new_title: str
    ) -> Dict[str, Any]:
        """
        Update conversation title
        
        Args:
            conversation_id: Conversation ID
            user_id: User updating the title
            new_title: New conversation title
            
        Returns:
            Updated conversation data
        """
        try:
            # Get conversation data
            conversation_data = await self._get_cached_conversation_data(conversation_id)
            
            if not conversation_data:
                raise ChatServiceError(f"Conversation not found: {conversation_id}")
            
            # Validate user access (creator or participant)
            if user_id not in conversation_data.get("participants", []):
                raise ChatServiceError("Access denied to conversation")
            
            # Validate title
            if not new_title or len(new_title.strip()) == 0:
                raise ChatServiceError("Title cannot be empty")
            
            if len(new_title) > self.title_max_length:
                raise ChatServiceError(f"Title too long (max {self.title_max_length} characters)")
            
            # Update title
            conversation_data["title"] = new_title.strip()
            conversation_data["updated_at"] = datetime.utcnow().isoformat()
            conversation_data["auto_titled"] = False  # Manual title override
            
            # Update cache
            await self._cache_conversation_data(conversation_id, conversation_data)
            
            # Track title update
            await self._track_conversation_event(conversation_id, "title_updated", user_id)
            
            return {
                "conversation": conversation_data,
                "message": "Title updated successfully"
            }
            
        except Exception as e:
            print(f"Failed to update conversation title {conversation_id}: {e}")
            raise ChatServiceError(f"Failed to update title: {str(e)}")
    
    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: str,
        soft_delete: bool = True
    ) -> Dict[str, Any]:
        """
        Delete conversation
        
        Args:
            conversation_id: Conversation ID
            user_id: User requesting deletion
            soft_delete: Whether to soft delete or permanently delete
            
        Returns:
            Deletion result
        """
        try:
            # Get conversation data
            conversation_data = await self._get_cached_conversation_data(conversation_id)
            
            if not conversation_data:
                raise ChatServiceError(f"Conversation not found: {conversation_id}")
            
            # Validate user access (creator only for deletion)
            if conversation_data.get("creator_id") != user_id:
                raise ChatServiceError("Only conversation creator can delete")
            
            if soft_delete:
                # Soft delete - mark as inactive
                conversation_data["is_active"] = False
                conversation_data["deleted_at"] = datetime.utcnow().isoformat()
                conversation_data["deleted_by"] = user_id
                
                await self._cache_conversation_data(conversation_id, conversation_data)
                
                result = {
                    "conversation_id": conversation_id,
                    "action": "soft_deleted",
                    "deleted_at": conversation_data["deleted_at"]
                }
            else:
                # Hard delete - remove from cache and storage
                await redis_service.delete(f"conversation:{conversation_id}")
                await redis_service.delete(f"messages:{conversation_id}")
                
                result = {
                    "conversation_id": conversation_id,
                    "action": "hard_deleted",
                    "deleted_at": datetime.utcnow().isoformat()
                }
            
            # Track deletion
            await self._track_conversation_event(conversation_id, "deleted", user_id)
            
            return result
            
        except Exception as e:
            print(f"Failed to delete conversation {conversation_id}: {e}")
            raise ChatServiceError(f"Failed to delete conversation: {str(e)}")
    
    async def search_conversations(
        self,
        user_id: str,
        query: str,
        conversation_id: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search within conversations and messages
        
        Args:
            user_id: User performing the search
            query: Search query
            conversation_id: Optional specific conversation to search
            limit: Maximum results to return
            
        Returns:
            Search results
        """
        try:
            print(f"[{datetime.utcnow()}] Searching conversations for user {user_id}: '{query}'")
            
            search_results = []
            
            if conversation_id:
                # Search within specific conversation
                conversation_results = await self._search_conversation_messages(
                    conversation_id, user_id, query, limit
                )
                search_results.extend(conversation_results)
            else:
                # Search across all user's conversations
                user_conversations = await self._get_user_conversations(user_id, 100, 0)
                
                for conv in user_conversations:
                    conv_results = await self._search_conversation_messages(
                        conv["id"], user_id, query, limit // len(user_conversations) + 1
                    )
                    search_results.extend(conv_results)
            
            # Sort by relevance and recency
            search_results.sort(key=lambda x: (x["relevance_score"], x["timestamp"]), reverse=True)
            
            # Limit results
            search_results = search_results[:limit]
            
            return {
                "results": search_results,
                "query": query,
                "total_found": len(search_results),
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            print(f"Search failed for user {user_id}: {e}")
            raise ChatServiceError(f"Search failed: {str(e)}")
    
    async def export_conversation(
        self,
        conversation_id: str,
        user_id: str,
        format: str = "json",
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Export conversation to various formats
        
        Args:
            conversation_id: Conversation ID to export
            user_id: User requesting export
            format: Export format (json, txt, pdf)
            include_metadata: Whether to include metadata
            
        Returns:
            Export data or file path
        """
        try:
            # Validate access
            conversation_data = await self._get_cached_conversation_data(conversation_id)
            
            if not conversation_data:
                raise ChatServiceError(f"Conversation not found: {conversation_id}")
            
            if user_id not in conversation_data.get("participants", []):
                raise ChatServiceError("Access denied to conversation")
            
            # Get all messages
            messages = await self._get_conversation_messages(conversation_id, self.max_messages_per_conversation)
            
            # Prepare export data
            export_data = {
                "conversation": conversation_data,
                "messages": messages,
                "exported_at": datetime.utcnow().isoformat(),
                "exported_by": user_id,
                "format": format
            }
            
            if not include_metadata:
                # Remove metadata from conversation and messages
                export_data["conversation"].pop("metadata", None)
                for msg in export_data["messages"]:
                    msg.pop("metadata", None)
            
            # Format-specific processing
            if format == "json":
                result = {
                    "export_type": "json",
                    "data": export_data,
                    "filename": f"conversation_{conversation_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                }
            
            elif format == "txt":
                # Convert to plain text
                text_content = self._format_conversation_as_text(export_data)
                result = {
                    "export_type": "txt",
                    "content": text_content,
                    "filename": f"conversation_{conversation_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
                }
            
            elif format == "pdf":
                # PDF export (mock implementation)
                result = {
                    "export_type": "pdf",
                    "message": "PDF export queued - download link will be sent via email",
                    "filename": f"conversation_{conversation_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
                }
            
            else:
                raise ChatServiceError(f"Unsupported export format: {format}")
            
            # Track export
            await self._track_conversation_event(conversation_id, "exported", user_id)
            
            return result
            
        except Exception as e:
            print(f"Export failed for conversation {conversation_id}: {e}")
            raise ChatServiceError(f"Export failed: {str(e)}")
    
    # Private helper methods
    
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID"""
        return f"conv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        return f"msg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    async def _cache_conversation_data(self, conversation_id: str, data: Dict[str, Any]) -> None:
        """Cache conversation data"""
        cache_key = f"conversation:{conversation_id}"
        await redis_service.set(cache_key, data, self.conversation_cache_ttl)
    
    async def _get_cached_conversation_data(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get cached conversation data"""
        cache_key = f"conversation:{conversation_id}"
        return await redis_service.get(cache_key)
    
    async def _store_message(self, message_data: Dict[str, Any]) -> None:
        """Store message data"""
        conversation_id = message_data["conversation_id"]
        message_id = message_data["id"]
        
        # Store in conversation's message list
        messages_key = f"messages:{conversation_id}"
        await redis_service.lpush(messages_key, message_data)
        await redis_service.expire(messages_key, self.conversation_cache_ttl)
        
        # Cache individual message
        message_key = f"message:{message_id}"
        await redis_service.set(message_key, message_data, self.message_cache_ttl)
    
    async def _update_conversation_after_message(
        self,
        conversation_id: str,
        message_data: Dict[str, Any]
    ) -> None:
        """Update conversation after new message"""
        conversation_data = await self._get_cached_conversation_data(conversation_id)
        
        if conversation_data:
            conversation_data["updated_at"] = datetime.utcnow().isoformat()
            conversation_data["last_activity"] = datetime.utcnow().isoformat()
            conversation_data["message_count"] = conversation_data.get("message_count", 0) + 1
            
            await self._cache_conversation_data(conversation_id, conversation_data)
    
    async def _maybe_auto_title_conversation(
        self,
        conversation_id: str,
        conversation_data: Dict[str, Any]
    ) -> None:
        """Auto-title conversation if conditions are met"""
        try:
            # Check if auto-titling should happen
            message_count = conversation_data.get("message_count", 0)
            auto_titled = conversation_data.get("auto_titled", False)
            
            if message_count >= self.auto_title_threshold and not auto_titled:
                # Get recent messages for context
                messages = await self._get_recent_messages(conversation_id, 5)
                
                if messages:
                    # Generate title using AI (mock implementation)
                    new_title = await self._generate_ai_title(messages)
                    
                    if new_title:
                        conversation_data["title"] = new_title
                        conversation_data["auto_titled"] = True
                        conversation_data["updated_at"] = datetime.utcnow().isoformat()
                        
                        await self._cache_conversation_data(conversation_id, conversation_data)
                        
                        print(f"Auto-titled conversation {conversation_id}: '{new_title}'")
        
        except Exception as e:
            print(f"Auto-titling failed for conversation {conversation_id}: {e}")
    
    async def _generate_ai_title(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """Generate conversation title using AI"""
        try:
            # Prepare context from messages
            context = []
            for msg in messages[-5:]:  # Last 5 messages
                if msg.get("type") == MessageType.TEXT:
                    context.append(msg.get("content", ""))
            
            if not context:
                return None
            
            # Mock AI title generation (replace with actual AI service)
            combined_text = " ".join(context)
            
            # Simple title extraction (replace with proper AI)
            words = combined_text.split()[:10]  # First 10 words
            title = " ".join(words)
            
            if len(title) > self.title_max_length:
                title = title[:self.title_max_length - 3] + "..."
            
            return title or "Conversation"
            
        except Exception as e:
            print(f"AI title generation failed: {e}")
            return None
    
    async def _validate_message_content(self, content: str, message_type: MessageType) -> None:
        """Validate message content"""
        if not content or len(content.strip()) == 0:
            raise ChatServiceError("Message content cannot be empty")
        
        if len(content) > self.max_message_length:
            raise ChatServiceError(f"Message too long (max {self.max_message_length} characters)")
        
        # Additional validation based on message type
        if message_type == MessageType.TEXT:
            # Check for potentially harmful content (basic implementation)
            if any(word in content.lower() for word in ["spam", "malicious"]):
                raise ChatServiceError("Message contains inappropriate content")
    
    async def _track_conversation_event(self, conversation_id: str, event: str, user_id: str) -> None:
        """Track conversation analytics event"""
        event_data = {
            "conversation_id": conversation_id,
            "event": event,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        analytics_key = f"analytics:conversation:{conversation_id}"
        await redis_service.lpush(analytics_key, event_data)
        await redis_service.expire(analytics_key, 86400 * 30)  # 30 days
    
    async def _get_user_conversations(
        self,
        user_id: str,
        limit: int,
        offset: int,
        conversation_type: Optional[ConversationType] = None,
        search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user's conversations (mock implementation)"""
        # Mock implementation - replace with actual database query
        mock_conversations = []
        
        for i in range(limit):
            conv_id = f"conv_mock_{i + offset}"
            mock_conversations.append({
                "id": conv_id,
                "title": f"Mock Conversation {i + offset}",
                "type": conversation_type or ConversationType.GENERAL,
                "creator_id": user_id,
                "participants": [user_id],
                "created_at": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "updated_at": (datetime.utcnow() - timedelta(minutes=i * 10)).isoformat(),
                "message_count": 5 + i,
                "is_active": True
            })
        
        # Apply filters
        if conversation_type:
            mock_conversations = [c for c in mock_conversations if c["type"] == conversation_type]
        
        if search_query:
            mock_conversations = [c for c in mock_conversations if search_query.lower() in c["title"].lower()]
        
        return mock_conversations
    
    async def _get_conversation_messages(
        self,
        conversation_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get conversation messages"""
        messages_key = f"messages:{conversation_id}"
        messages = await redis_service.lrange(messages_key, 0, limit - 1)
        return messages or []
    
    async def _get_recent_messages(self, conversation_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent messages from conversation"""
        return await self._get_conversation_messages(conversation_id, limit)
    
    async def _get_unread_count(self, conversation_id: str, user_id: str) -> int:
        """Get unread message count for user (mock implementation)"""
        # Mock implementation
        return 2
    
    async def _update_last_read(self, conversation_id: str, user_id: str) -> None:
        """Update user's last read timestamp"""
        last_read_key = f"last_read:{conversation_id}:{user_id}"
        await redis_service.set(last_read_key, datetime.utcnow().isoformat(), 86400 * 7)
    
    async def _search_conversation_messages(
        self,
        conversation_id: str,
        user_id: str,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search messages within a conversation"""
        # Mock search implementation
        messages = await self._get_conversation_messages(conversation_id, 100)
        
        search_results = []
        for msg in messages:
            if query.lower() in msg.get("content", "").lower():
                search_results.append({
                    "conversation_id": conversation_id,
                    "message_id": msg["id"],
                    "content": msg["content"],
                    "sender_id": msg["sender_id"],
                    "timestamp": msg["created_at"],
                    "relevance_score": 0.8,  # Mock relevance
                    "context": msg.get("content", "")[:200]  # Context snippet
                })
        
        return search_results[:limit]
    
    def _format_conversation_as_text(self, export_data: Dict[str, Any]) -> str:
        """Format conversation as plain text"""
        conversation = export_data["conversation"]
        messages = export_data["messages"]
        
        text_lines = [
            f"Conversation: {conversation['title']}",
            f"Created: {conversation['created_at']}",
            f"Participants: {', '.join(conversation['participants'])}",
            "-" * 50,
            ""
        ]
        
        for msg in messages:
            timestamp = msg["created_at"]
            sender = msg["sender_id"]
            content = msg["content"]
            
            text_lines.append(f"[{timestamp}] {sender}: {content}")
        
        return "\n".join(text_lines)

# Global chat service instance
chat_service = ChatService()