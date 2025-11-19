# Knowledge Agent
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..core.a2a import A2AProtocol
from ..schemas import AgentMessage, KnowledgePayload
from ..tools.web_search_tool import WebSearchTool
from ..core.llm_service import get_llm_service
from ..core.memory_bank import MemoryBank
from ..core.context_compactor import get_compactor

logger = structlog.get_logger()

class KnowledgeAgent:
    def __init__(self):
        logger.info("KnowledgeAgent initialized")
        self.web_search_tool = WebSearchTool()
        self.llm_service = get_llm_service()
        self.memory_bank = MemoryBank()
        self.compactor = get_compactor()
    
    async def search_knowledge(self, query: str, user_id: str = "default", web_search_tool: WebSearchTool = None) -> AgentMessage:
        """Search knowledge using web search and vector retrieval"""
        logger.info("Searching knowledge", query=query, user_id=user_id)
        
        # Use provided web search tool or default
        search_tool = web_search_tool or self.web_search_tool
        
        # Retrieve relevant context from vector DB
        context = self.memory_bank.retrieve_relevant_context(user_id, query, k=3)
        
        # Perform web search
        search_results = search_tool.search(query, max_results=5)
        
        # Extract relevant information from search results
        knowledge_results = []
        for result in search_results:
            knowledge_entry = {
                "title": result["title"],
                "url": result["url"],
                "snippet": result["snippet"],
                "relevance": result.get("relevance", 0.8)  # Default relevance if not provided
            }
            knowledge_results.append(knowledge_entry)
        
        # Add vector search results to knowledge
        if context and len(context) > 0:
            for ctx in context:
                knowledge_entry = {
                    "title": f"Memory: {ctx.get('source', 'Unknown')}",
                    "url": f"memory://{ctx.get('source', 'unknown')}",
                    "snippet": ctx["content"][:200] + "..." if len(ctx["content"]) > 200 else ctx["content"],
                    "relevance": ctx.get("score", 0.7)
                }
                knowledge_results.append(knowledge_entry)
        
        # Sort by relevance
        knowledge_results.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Generate knowledge summary using LLM
        summary = ""
        try:
            if context and len(context) > 0:
                context_text = "\n".join([ctx["content"] for ctx in context])
                summary = self.llm_service.generate_knowledge_response(query, context_text)
            else:
                # Generate summary from web search results
                search_text = "\n".join([f"{r['title']}: {r['snippet']}" for r in search_results])
                summary = self.llm_service.generate_text(
                    f"Summarize these search results for query: {query}\n\n{search_text}",
                    max_tokens=500
                )
        except Exception as e:
            logger.error("Failed to generate knowledge summary", error=str(e))
            summary = f"Found {len(knowledge_results)} relevant results for '{query}'"
        
        # Store search in memory
        self.memory_bank.store_memory(
            user_id=user_id,
            key=f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            value={
                "query": query,
                "results_count": len(knowledge_results),
                "summary": summary,
                "created_at": datetime.now().isoformat()
            },
            category="knowledge"
        )
        
        # Upsert search results to vector DB for future retrieval
        for result in search_results[:3]:  # Store top 3 results
            doc_id = f"web_{result['url'].replace('/', '_').replace(':', '_')}"
            content = f"{result['title']}\n{result['snippet']}"
            self.memory_bank.upsert_document(
                user_id=user_id,
                doc_id=doc_id,
                content=content,
                metadata={
                    "source": result["url"],
                    "title": result["title"],
                    "type": "web_search",
                    "relevance": result.get("relevance", 0.8)
                }
            )
        
        # Create knowledge payload
        knowledge_payload = KnowledgePayload(
            query=query,
            results=knowledge_results,
            sources=[result["url"] for result in search_results],
            summary=summary,
            context_used=bool(context),
            llm_generated=bool(summary)
        )
        
        # Create response message
        response = A2AProtocol.create_message(
            sender="knowledge",
            receiver="router",
            message_type="KNOWLEDGE_RESPONSE",
            payload=knowledge_payload.dict()
        )
        
        logger.info("Knowledge search completed", query=query, results_count=len(knowledge_results), context_used=bool(context))
        return response
    
    async def get_detailed_content(self, url: str, web_search_tool: WebSearchTool = None) -> str:
        """Get detailed content from a URL"""
        logger.info("Getting detailed content", url=url)
        
        search_tool = web_search_tool or self.web_search_tool
        content = search_tool.get_page_content(url)
        
        logger.info("Content retrieved", url=url, content_length=len(content))
        return content