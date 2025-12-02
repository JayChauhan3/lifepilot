# Memory Agent
import structlog
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..core.a2a import A2AProtocol
from ..core.memory_bank import MemoryBank
from ..core.llm_service import get_llm_service
from ..schemas import AgentMessage, MemoryPayload

logger = structlog.get_logger()

class MemoryAgent:
    def __init__(self):
        logger.info("MemoryAgent initialized")
        from ..core.memory_bank import get_memory_bank
        self.memory_bank = get_memory_bank()
        self.llm_service = get_llm_service()
    
    async def store_memory(self, user_id: str, key: str, value: Any, category: str = "general") -> AgentMessage:
        """Store a memory entry using MemoryBank"""
        logger.info("Storing memory", user_id=user_id, key=key, category=category)
        
        # Store in memory bank (includes vector DB)
        success = await self.memory_bank.store_memory(user_id, key, value, category)
        
        if success:
            memory_payload = MemoryPayload(
                user_id=user_id,
                memory_key=key,
                memory_value=value,
                action="stored",
                category=category,
                vector_stored=True
            )
            
            response = A2AProtocol.create_message(
                sender="memory",
                receiver="router",
                message_type="MEMORY_RESPONSE",
                payload=memory_payload.dict()
            )
            
            logger.info("Memory stored successfully", user_id=user_id, key=key)
        else:
            # Create error response
            memory_payload = MemoryPayload(
                user_id=user_id,
                memory_key=key,
                memory_value=None,
                action="error",
                category=category
            )
            
            response = A2AProtocol.create_message(
                sender="memory",
                receiver="router",
                message_type="MEMORY_ERROR",
                payload=memory_payload.dict()
            )
            
            logger.error("Failed to store memory", user_id=user_id, key=key)
        
        return response
    
    async def retrieve_memory(self, user_id: str, key: str) -> AgentMessage:
        """Retrieve a memory entry from MemoryBank"""
        logger.info("Retrieving memory", user_id=user_id, key=key)
        
        # Retrieve from memory bank
        value = await self.memory_bank.get_memory(user_id, key)
        
        if value is not None:
            memory_payload = MemoryPayload(
                user_id=user_id,
                memory_key=key,
                memory_value=value,
                action="retrieved",
                category="general"
            )
            
            response = A2AProtocol.create_message(
                sender="memory",
                receiver="router",
                message_type="MEMORY_RESPONSE",
                payload=memory_payload.dict()
            )
            
            logger.info("Memory retrieved successfully", user_id=user_id, key=key)
        else:
            memory_payload = MemoryPayload(
                user_id=user_id,
                memory_key=key,
                memory_value=None,
                action="not_found",
                category="general"
            )
            
            response = A2AProtocol.create_message(
                sender="memory",
                receiver="router",
                message_type="MEMORY_RESPONSE",
                payload=memory_payload.dict()
            )
            
            logger.info("Memory not found", user_id=user_id, key=key)
        
        return response
    
    async def get_memories_by_category(self, user_id: str, category: str) -> AgentMessage:
        """Get all memories in a specific category"""
        logger.info("Getting memories by category", user_id=user_id, category=category)
        
        memories = self.memory_bank.get_memories_by_category(user_id, category)
        
        memory_payload = MemoryPayload(
            user_id=user_id,
            memory_key=f"category_{category}",
            memory_value=memories,
            action="retrieved_category",
            category=category
        )
        
        response = A2AProtocol.create_message(
            sender="memory",
            receiver="router",
            message_type="MEMORY_RESPONSE",
            payload=memory_payload.dict()
        )
        
        logger.info("Category memories retrieved", user_id=user_id, category=category, count=len(memories))
        return response
    
    async def search_memories(self, user_id: str, query: str) -> AgentMessage:
        """Search memories by query string"""
        logger.info("Searching memories", user_id=user_id, query=query)
        
        results = self.memory_bank.search_memories(user_id, query)
        
        memory_payload = MemoryPayload(
            user_id=user_id,
            memory_key=f"search_{query}",
            memory_value=results,
            action="search_results",
            category="search"
        )
        
        response = A2AProtocol.create_message(
            sender="memory",
            receiver="router",
            message_type="MEMORY_RESPONSE",
            payload=memory_payload.dict()
        )
        
        logger.info("Memory search completed", user_id=user_id, query=query, results_count=len(results))
        return response
    
    async def search_similar_memories(self, user_id: str, query: str, k: int = 5) -> AgentMessage:
        """Search memories using vector similarity"""
        logger.info("Searching similar memories", user_id=user_id, query=query, k=k)
        
        # Use vector search
        similar_memories = self.memory_bank.retrieve_similar_memories(user_id, query, k)
        
        # Generate summary using LLM
        summary = ""
        if similar_memories:
            try:
                summary = self.llm_service.generate_memory_summary(similar_memories)
            except Exception as e:
                logger.error("Failed to generate memory summary", error=str(e))
                summary = f"Found {len(similar_memories)} similar memories"
        
        memory_payload = MemoryPayload(
            user_id=user_id,
            memory_key=f"vector_search_{query}",
            memory_value=similar_memories,
            action="vector_search_results",
            category="search",
            summary=summary,
            vector_search=True
        )
        
        response = A2AProtocol.create_message(
            sender="memory",
            receiver="router",
            message_type="MEMORY_RESPONSE",
            payload=memory_payload.dict()
        )
        
        logger.info("Vector memory search completed", user_id=user_id, query=query, results_count=len(similar_memories))
        return response
    
    async def index_document(self, user_id: str, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> AgentMessage:
        """Index a document for vector search"""
        logger.info("Indexing document", user_id=user_id, doc_id=doc_id)
        
        # Upsert to vector DB
        success = self.memory_bank.upsert_document(user_id, doc_id, content, metadata)
        
        if success:
            memory_payload = MemoryPayload(
                user_id=user_id,
                memory_key=doc_id,
                memory_value={"content": content[:100] + "...", "metadata": metadata},
                action="indexed",
                category="document",
                vector_stored=True
            )
            
            response = A2AProtocol.create_message(
                sender="memory",
                receiver="router",
                message_type="MEMORY_RESPONSE",
                payload=memory_payload.dict()
            )
            
            logger.info("Document indexed successfully", user_id=user_id, doc_id=doc_id)
        else:
            # Create error response
            memory_payload = MemoryPayload(
                user_id=user_id,
                memory_key=doc_id,
                memory_value=None,
                action="error",
                category="document"
            )
            
            response = A2AProtocol.create_message(
                sender="memory",
                receiver="router",
                message_type="MEMORY_ERROR",
                payload=memory_payload.dict()
            )
            
            logger.error("Failed to index document", user_id=user_id, doc_id=doc_id)
        
        return response