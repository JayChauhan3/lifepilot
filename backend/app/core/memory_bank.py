# Memory Bank
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import os
import uuid
from pinecone import Pinecone
from .embeddings import get_embeddings
from .context_compactor import get_compactor

logger = structlog.get_logger()

class MemoryBank:
    """Central memory storage for agents with vector DB support"""
    
    def __init__(self):
        logger.info("MemoryBank initialized")
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.global_memory: Dict[str, Any] = {}
        
        # Database setup
        from .database import get_database
        self.db = get_database()
        self.collection = None
        if self.db is not None:
            self.collection = self.db.memories
            logger.info("MongoDB memories collection initialized")
        else:
            logger.warning("MongoDB not available, falling back to in-memory storage")
        
        # Vector DB setup
        self.vector_db_provider = os.getenv("VECTOR_DB_PROVIDER", "pinecone")
        self.embeddings = get_embeddings()
        self.compactor = get_compactor()
        self._vector_client = None
        self._vector_index = None
        
        # Initialize vector DB
        self._initialize_vector_db()
        
        # Load memories from DB if available
        # We don't load everything into RAM at start to avoid memory issues with large datasets
        # Instead we'll query on demand
    
    def _initialize_vector_db(self):
        """Initialize vector database client"""
        try:
            if self.vector_db_provider == "pinecone":
                # Initialize Pinecone
                api_key = os.getenv("PINECONE_API_KEY")
                index_name = os.getenv("PINECONE_INDEX", "lifepilot-memory")
                
                if not api_key:
                    logger.warning("PINECONE_API_KEY not set, running without vector DB")
                    return

                self._vector_client = Pinecone(api_key=api_key)
                self._vector_index = self._vector_client.Index(index_name)
                
                logger.info("Pinecone initialized", index=index_name)
            else:
                logger.error("Unsupported vector DB provider", provider=self.vector_db_provider)
                # raise ValueError(f"Unsupported vector DB provider: {self.vector_db_provider}")
        except Exception as e:
            logger.error("Failed to initialize vector DB", error=str(e))
            # Continue without vector DB
            self._vector_client = None
            self._vector_index = None
    
    async def store_memory(self, user_id: str, key: str, value: Any, category: str = "general") -> bool:
        """Store a memory with category and timestamp"""
        try:
            memory_entry = {
                "value": value,
                "category": category,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "user_id": user_id,
                "key": key
            }
            
            # Update in-memory cache
            if user_id not in self.memories:
                self.memories[user_id] = {}
            self.memories[user_id][key] = memory_entry
            
            # Store in MongoDB
            if self.collection is not None:
                await self.collection.update_one(
                    {"user_id": user_id, "key": key},
                    {"$set": memory_entry},
                    upsert=True
                )
                logger.info("Memory stored in MongoDB", user_id=user_id, key=key)
            
            # Store in Vector DB if applicable
            if self._vector_index and isinstance(value, str):
                try:
                    vector = self.embeddings.get_embedding(value)
                    self._vector_index.upsert(vectors=[(
                        f"{user_id}_{key}",
                        vector,
                        {"user_id": user_id, "category": category, "content": value}
                    )])
                except Exception as e:
                    logger.error("Failed to store in vector DB", error=str(e))
            
            return True
        except Exception as e:
            logger.error("Failed to store memory", error=str(e))
            return False
    
    async def get_memory(self, user_id: str, key: str) -> Optional[Any]:
        """Retrieve a specific memory"""
        # Try cache first
        if user_id in self.memories and key in self.memories[user_id]:
            return self.memories[user_id][key]["value"]
            
        # Try MongoDB
        if self.collection is not None:
            doc = await self.collection.find_one({"user_id": user_id, "key": key})
            if doc:
                # Update cache
                if user_id not in self.memories:
                    self.memories[user_id] = {}
                self.memories[user_id][key] = doc
                return doc["value"]
            
        return None

    async def get_memories_by_category(self, user_id: str, category: str) -> Dict[str, Any]:
        """Get all memories in a category for a user"""
        filtered_memories = {}
        
        # Try MongoDB first (source of truth)
        if self.collection is not None:
            cursor = self.collection.find({"user_id": user_id, "category": category})
            async for doc in cursor:
                filtered_memories[doc["key"]] = doc["value"]
                # Update cache
                if user_id not in self.memories:
                    self.memories[user_id] = {}
                self.memories[user_id][doc["key"]] = doc
        else:
            # Fallback to cache
            if user_id in self.memories:
                for key, memory_entry in self.memories[user_id].items():
                    if memory_entry["category"] == category:
                        filtered_memories[key] = memory_entry["value"]
        
        logger.info("Memories retrieved by category", user_id=user_id, category=category, count=len(filtered_memories))
        return filtered_memories
    
    async def get_all_memories(self, user_id: str) -> Dict[str, Any]:
        """Get all memories for a user"""
        all_memories = {}
        
        # Try MongoDB
        if self.collection is not None:
            cursor = self.collection.find({"user_id": user_id})
            async for doc in cursor:
                all_memories[doc["key"]] = doc["value"]
                # Update cache
                if user_id not in self.memories:
                    self.memories[user_id] = {}
                self.memories[user_id][doc["key"]] = doc
        else:
            # Fallback to cache
            if user_id in self.memories:
                for key, memory_entry in self.memories[user_id].items():
                    all_memories[key] = memory_entry["value"]
        
        logger.info("All memories retrieved", user_id=user_id, count=len(all_memories))
        return all_memories
    
    async def delete_memory(self, user_id: str, key: str) -> bool:
        """Delete a specific memory"""
        success = False
        
        # Delete from MongoDB
        if self.collection is not None:
            result = await self.collection.delete_one({"user_id": user_id, "key": key})
            if result.deleted_count > 0:
                success = True
        
        # Delete from cache
        if user_id in self.memories and key in self.memories[user_id]:
            del self.memories[user_id][key]
            success = True
            
        if success:
            logger.info("Memory deleted", user_id=user_id, key=key)
            
        return success
    

    
    def store_global_memory(self, key: str, value: Any) -> bool:
        """Store global memory accessible to all agents"""
        try:
            self.global_memory[key] = {
                "value": value,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            logger.info("Global memory stored", key=key)
            return True
        except Exception as e:
            logger.error("Failed to store global memory", key=key, error=str(e))
            return False
    
    def get_global_memory(self, key: str) -> Optional[Any]:
        """Retrieve global memory"""
        if key in self.global_memory:
            logger.info("Global memory retrieved", key=key)
            return self.global_memory[key]["value"]
        return None
    
    def search_memories(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """Search memories by query string"""
        if user_id not in self.memories:
            return []
        
        results = []
        query_lower = query.lower()
        
        for key, memory_entry in self.memories[user_id].items():
            # Search in key and value
            if query_lower in key.lower() or query_lower in str(memory_entry["value"]).lower():
                results.append({
                    "key": key,
                    "value": memory_entry["value"],
                    "category": memory_entry["category"],
                    "created_at": memory_entry["created_at"]
                })
        
        logger.info("Memory search completed", user_id=user_id, query=query, results_count=len(results))
        return results
    
    def _upsert_memory_vector(self, user_id: str, key: str, value: Any, category: str):
        """Upsert memory into vector DB"""
        try:
            if not self._vector_index:
                return

            # Convert value to string for embedding
            content = str(value)
            
            # Generate embedding
            embedding = self.embeddings.embed_single(content)
            
            # Upsert into Pinecone
            self._vector_index.upsert(
                vectors=[{
                    "id": key,
                    "values": embedding,
                    "metadata": {
                        "user_id": user_id,
                        "key": key,
                        "category": category,
                        "created_at": datetime.now().isoformat(),
                        "content": content # Store content in metadata for retrieval
                    }
                }]
            )
            
            logger.debug("Memory upserted to vector DB", user_id=user_id, key=key)
        except Exception as e:
            logger.error("Failed to upsert memory vector", user_id=user_id, key=key, error=str(e))
    
    def retrieve_similar_memories(self, user_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories similar to query using vector search"""
        if not self._vector_index:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_single(query)
            
            # Search Pinecone
            results = self._vector_index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True,
                filter={"user_id": user_id}
            )
            
            # Format results
            memories = []
            for match in results.matches:
                memory = {
                    "key": match.id,
                    "content": match.metadata.get("content", ""),
                    "metadata": match.metadata,
                    "distance": match.score if match.score else 0 # Pinecone returns similarity score
                }
                memories.append(memory)
            
            logger.info("Similar memories retrieved", user_id=user_id, query=query, count=len(memories))
            return memories
            
        except Exception as e:
            logger.error("Failed to retrieve similar memories", user_id=user_id, query=query, error=str(e))
            return []
    
    def upsert_document(self, user_id: str, doc_id: str, content: str, metadata: Dict[str, Any] = None):
        """Upsert a document into vector DB for RAG"""
        if not self._vector_index:
            return False
        
        try:
            # Generate embedding
            embedding = self.embeddings.embed_single(content)
            
            # Prepare metadata
            doc_metadata = {
                "user_id": user_id,
                "doc_id": doc_id,
                "type": "document",
                "created_at": datetime.now().isoformat(),
                "content": content # Store content in metadata
            }
            if metadata:
                doc_metadata.update(metadata)
            
            # Upsert
            self._vector_index.upsert(
                vectors=[{
                    "id": doc_id,
                    "values": embedding,
                    "metadata": doc_metadata
                }]
            )
            
            logger.info("Document upserted", user_id=user_id, doc_id=doc_id)
            return True
            
        except Exception as e:
            logger.error("Failed to upsert document", user_id=user_id, doc_id=doc_id, error=str(e))
            return False
    
    def retrieve_relevant_context(self, user_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context for RAG pipeline"""
        contexts = []
        
        # Get similar memories
        memories = self.retrieve_similar_memories(user_id, query, k)
        for memory in memories:
            contexts.append({
                "content": memory["content"],
                "source": f"memory:{memory['key']}",
                "type": "memory",
                "score": 1 - memory.get("distance", 0),
                "metadata": memory["metadata"]
            })
        
        # Get relevant documents if available
        try:
            if self._vector_index:
                query_embedding = self.embeddings.embed_single(query)
                
                doc_results = self._vector_index.query(
                    vector=query_embedding,
                    top_k=k,
                    include_metadata=True,
                    filter={"user_id": user_id, "type": "document"}
                )
                
                for match in doc_results.matches:
                    contexts.append({
                        "content": match.metadata.get("content", ""),
                        "source": f"document:{match.id}",
                        "type": "document",
                        "score": match.score if match.score else 0,
                        "metadata": match.metadata
                    })
        except:
            pass  # No documents found
        
        # Sort by relevance
        contexts.sort(key=lambda x: x["score"], reverse=True)
        
# Global MemoryBank instance
_memory_bank = None

def get_memory_bank() -> MemoryBank:
    """Get global MemoryBank instance"""
    global _memory_bank
    if _memory_bank is None:
        _memory_bank = MemoryBank()
    return _memory_bank

def reset_memory_bank():
    """Reset MemoryBank instance (for testing)"""
    global _memory_bank
    _memory_bank = None