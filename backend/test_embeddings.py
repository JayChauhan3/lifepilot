#!/usr/bin/env python3
"""Test embeddings and RAG functionality"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.embeddings import get_embeddings
from app.core.memory_bank import MemoryBank
from app.core.context_compactor import get_compactor
from app.core.llm_service import get_llm_service
from app.agents.planner import PlannerAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.memory import MemoryAgent

async def test_embeddings():
    """Test embeddings generation"""
    print("\n=== Testing Embeddings ===")
    
    embeddings = get_embeddings()
    
    # Test single embedding
    text = "This is a test sentence for embeddings."
    embedding = embeddings.embed_single(text)
    print(f"Generated embedding for: '{text}'")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    
    # Test batch embeddings
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Python is a popular programming language"
    ]
    embeddings_batch = embeddings.embed(texts)
    print(f"\nGenerated {len(embeddings_batch)} embeddings")
    print(f"All embeddings have same dimension: {all(len(e) == len(embedding) for e in embeddings_batch)}")
    
    # Test similarity
    similarities = embeddings.compute_similarity(embeddings_batch[0], embeddings_batch[1:])
    print(f"\nSimilarity between first and second texts: {similarities[0]:.4f}")
    
    # Test search
    query = "AI and machine learning"
    query_embedding = embeddings.embed_single(query)
    results = embeddings.search_similar(query, embeddings_batch, top_k=2)
    print(f"\nSearch results for '{query}':")
    for i, (idx, score) in enumerate(results, 1):
        print(f"  {i}. {texts[idx][:50]}... (score: {score:.4f})")

async def test_memory_bank():
    """Test MemoryBank with vector DB"""
    print("\n\n=== Testing MemoryBank ===")
    
    memory_bank = MemoryBank()
    user_id = "test_user"
    
    # Store memories
    memories = [
        ("meeting_1", "Team meeting scheduled for tomorrow at 2 PM", "calendar"),
        ("project_status", "Current project is 75% complete, on track for deadline", "work"),
        ("idea", "Consider implementing a notification system for deadlines", "ideas"),
        ("note", "Remember to review the quarterly report", "notes")
    ]
    
    for key, value, category in memories:
        success = memory_bank.store_memory(user_id, key, value, category)
        print(f"Stored memory '{key}': {'✓' if success else '✗'}")
    
    # Test basic retrieval
    print("\n--- Basic Retrieval ---")
    for key, _, _ in memories:
        value = memory_bank.get_memory(user_id, key)
        print(f"Retrieved '{key}': {value[:50]}..." if value else f"Not found: {key}")
    
    # Test keyword search
    print("\n--- Keyword Search ---")
    search_results = memory_bank.search_memories(user_id, "project")
    print(f"Found {len(search_results)} memories with 'project'")
    for result in search_results:
        print(f"  - {result['key']}: {result['value'][:50]}...")
    
    # Test vector search
    print("\n--- Vector Search ---")
    similar_memories = memory_bank.retrieve_similar_memories(user_id, "work progress", k=3)
    print(f"Found {len(similar_memories)} similar memories for 'work progress':")
    for memory in similar_memories:
        print(f"  - {memory['key']}: {memory['content'][:50]}... (similarity: {1-memory.get('distance', 0):.4f})")
    
    # Test document upsert
    print("\n--- Document Indexing ---")
    doc_content = """
    Project Alpha Status Report
    
    The project is currently in the implementation phase.
    Key milestones achieved:
    - Database design completed
    - API endpoints implemented
    - Frontend UI mockups approved
    
    Next steps:
    - Integration testing
    - Performance optimization
    - User acceptance testing
    
    Timeline: On track for Q4 delivery
    """
    
    doc_success = memory_bank.upsert_document(
        user_id=user_id,
        doc_id="project_alpha_report",
        content=doc_content,
        metadata={"type": "report", "date": "2024-01-15"}
    )
    print(f"Upserted document: {'✓' if doc_success else '✗'}")
    
    # Test context retrieval
    print("\n--- Context Retrieval ---")
    context = memory_bank.retrieve_relevant_context(user_id, "project status", k=5)
    print(f"Retrieved {len(context)} context items:")
    for ctx in context:
        print(f"  - {ctx['type']}: {ctx['source']} (score: {ctx['score']:.4f})")
        print(f"    {ctx['content'][:100]}...")

async def test_context_compactor():
    """Test context compactor"""
    print("\n\n=== Testing Context Compactor ===")
    
    compactor = get_compactor()
    
    # Create test context
    contexts = [
        {
            "content": "This is a short context item.",
            "source": "memory:note1",
            "type": "memory",
            "score": 0.9
        },
        {
            "content": "This is a much longer context item that contains a lot more detail and information that might be useful for understanding the broader context of the situation. It includes various facts and figures that contribute to the overall understanding.",
            "source": "document:doc1",
            "type": "document",
            "score": 0.8
        },
        {
            "content": "Another context item with medium length and some relevant information.",
            "source": "memory:note2",
            "type": "memory",
            "score": 0.7
        }
    ]
    
    # Test token counting
    for ctx in contexts:
        tokens = compactor.count_tokens(ctx["content"])
        print(f"Content ({ctx['source']}): {tokens} tokens")
    
    # Test compaction by token limit
    compacted = compactor.compact_by_token_limit(contexts, "What is the project status?")
    print(f"\nCompacted context (length: {len(compacted)} chars):")
    print(compacted[:200] + "..." if len(compacted) > 200 else compacted)
    
    # Test RAG prompt creation
    rag_prompt = compactor.create_rag_prompt("What is the project status?", contexts)
    print(f"\nRAG Prompt (length: {len(rag_prompt)} chars):")
    print(rag_prompt[:500] + "..." if len(rag_prompt) > 500 else rag_prompt)

async def test_llm_service():
    """Test LLM service"""
    print("\n\n=== Testing LLM Service ===")
    
    llm_service = get_llm_service()
    
    # Test text generation
    prompt = "Explain the concept of Retrieval-Augmented Generation in 2-3 sentences."
    response = llm_service.generate_text(prompt, max_tokens=200)
    print(f"LLM Response: {response}")
    
    # Test plan generation
    plan = llm_service.generate_plan("Create a personal productivity system")
    print(f"\nGenerated Plan:")
    print(f"Title: {plan.get('title', 'N/A')}")
    print(f"Description: {plan.get('description', 'N/A')}")
    print(f"Steps: {len(plan.get('steps', []))}")
    for i, step in enumerate(plan.get('steps', []), 1):
        if isinstance(step, dict):
            print(f"  {i}. {step.get('action', str(step))}")
        else:
            print(f"  {i}. {step}")
    
    # Test knowledge response
    context = "The project is 75% complete with key milestones achieved."
    knowledge = llm_service.generate_knowledge_response("What is the project status?", context)
    print(f"\nKnowledge Response: {knowledge}")

async def test_rag_pipeline():
    """Test full RAG pipeline with agents"""
    print("\n\n=== Testing RAG Pipeline ===")
    
    # Initialize agents
    planner = PlannerAgent()
    knowledge = KnowledgeAgent()
    memory = MemoryAgent()
    
    user_id = "test_user_rag"
    
    # Store some test memories
    await memory.store_memory(user_id, "project_goal", "Build an AI-powered task management system", "goals")
    await memory.store_memory(user_id, "current_task", "Implementing the RAG pipeline", "tasks")
    await memory.store_memory(user_id, "team_size", "Team has 5 developers", "team")
    
    # Test Planner with RAG
    print("\n--- Planner with RAG ---")
    plan_response = await planner.create_plan("Plan the next sprint for our AI project", user_id)
    plan_payload = plan_response.payload
    print(f"Plan generated: {'✓' if plan_response else '✗'}")
    print(f"Context used: {plan_payload.get('context_used', False)}")
    print(f"LLM generated: {plan_payload.get('llm_generated', False)}")
    print(f"Steps: {len(plan_payload.get('steps', []))}")
    
    # Test Knowledge with RAG
    print("\n--- Knowledge with RAG ---")
    knowledge_response = await knowledge.search_knowledge("best practices for AI development", user_id)
    knowledge_payload = knowledge_response.payload
    print(f"Knowledge search: {'✓' if knowledge_response else '✗'}")
    print(f"Results: {len(knowledge_payload.get('results', []))}")
    print(f"Context used: {knowledge_payload.get('context_used', False)}")
    print(f"Summary generated: {'✓' if knowledge_payload.get('summary') else '✗'}")
    
    # Test Memory vector search
    print("\n--- Memory Vector Search ---")
    memory_response = await memory.search_similar_memories(user_id, "development progress", k=3)
    memory_payload = memory_response.payload
    print(f"Vector search: {'✓' if memory_response else '✗'}")
    print(f"Similar memories: {len(memory_payload.get('memory_value', []))}")
    print(f"Summary: {memory_payload.get('summary', 'No summary')[:100]}...")

async def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Embeddings and RAG Implementation")
    print("=" * 60)
    
    # Set environment for testing
    os.environ["EMBEDDING_PROVIDER"] = "sentence-transformers"
    # Test Pinecone (mocked)
    os.environ["VECTOR_DB_PROVIDER"] = "pinecone"
    os.environ["LLM_PROVIDER"] = "mock"
    
    try:
        await test_embeddings()
        await test_memory_bank()
        await test_context_compactor()
        await test_llm_service()
        await test_rag_pipeline()
        
        print("\n\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
