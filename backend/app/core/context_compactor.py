# Context Compactor for RAG pipeline
import structlog
from typing import List, Dict, Any, Optional
import re
from collections import Counter
import tiktoken

logger = structlog.get_logger()

class ContextCompactor:
    """Compacts retrieved contexts for efficient LLM prompting"""
    
    def __init__(self, max_tokens: int = 2000, model: str = "gpt-3.5-turbo"):
        self.max_tokens = max_tokens
        self.model = model
        self.encoding = None
        self._initialize_tokenizer()
    
    def _initialize_tokenizer(self):
        """Initialize tokenizer for token counting"""
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Fallback to default encoding
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.warning("Using fallback tokenizer", model=self.model)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if not self.encoding:
            return len(text.split()) * 2  # Rough estimate
        return len(self.encoding.encode(text))
    
    def extractive_summary(self, texts: List[str], max_sentences: int = 5) -> str:
        """Extractive summarization based on sentence importance"""
        if not texts:
            return ""
        
        # Combine all texts
        combined_text = " ".join(texts)
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', combined_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return ". ".join(sentences)
        
        # Score sentences by word frequency
        word_freq = Counter()
        for sentence in sentences:
            words = sentence.lower().split()
            word_freq.update(words)
        
        sentence_scores = []
        for sentence in sentences:
            words = sentence.lower().split()
            score = sum(word_freq[word] for word in words if word in word_freq)
            sentence_scores.append((sentence, score))
        
        # Get top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in sentence_scores[:max_sentences]]
        
        # Preserve original order
        ordered_sentences = []
        for sentence in sentences:
            if sentence in top_sentences:
                ordered_sentences.append(sentence)
        
        return ". ".join(ordered_sentences)
    
    def compact_by_relevance(self, documents: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Compact documents based on relevance to query"""
        if not documents:
            return []
        
        # Score documents by relevance (simple keyword matching for now)
        query_words = set(query.lower().split())
        scored_docs = []
        
        for doc in documents:
            content = doc.get("content", "").lower()
            doc_words = set(content.split())
            
            # Calculate relevance score
            intersection = query_words.intersection(doc_words)
            score = len(intersection) / max(len(query_words), 1)
            
            scored_docs.append((doc, score))
        
        # Sort by relevance
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Return sorted documents
        return [doc[0] for doc in scored_docs]
    
    def compact_by_token_limit(self, documents: List[Dict[str, Any]], query: str = "") -> str:
        """Compact documents to fit within token limit"""
        if not documents:
            return ""
        
        # Sort by relevance if query provided
        if query:
            documents = self.compact_by_relevance(documents, query)
        
        # Build compacted context
        compacted_parts = []
        current_tokens = 0
        
        # Reserve tokens for system prompt and query
        reserved_tokens = 200 + self.count_tokens(query)
        available_tokens = self.max_tokens - reserved_tokens
        
        for doc in documents:
            content = doc.get("content", "")
            doc_tokens = self.count_tokens(content)
            
            # Add metadata
            metadata = f"[Source: {doc.get('source', 'Unknown')}]\n"
            metadata_tokens = self.count_tokens(metadata)
            total_tokens = doc_tokens + metadata_tokens
            
            if current_tokens + total_tokens <= available_tokens:
                compacted_parts.append(metadata + content)
                current_tokens += total_tokens
            else:
                # Try to add a truncated version
                remaining_tokens = available_tokens - current_tokens - metadata_tokens
                if remaining_tokens > 100:  # Only if meaningful amount remains
                    # Truncate content to fit
                    words = content.split()
                    truncated_words = []
                    word_count = 0
                    
                    for word in words:
                        word_tokens = self.count_tokens(word + " ")
                        if word_count + word_tokens <= remaining_tokens:
                            truncated_words.append(word)
                            word_count += word_tokens
                        else:
                            break
                    
                    if truncated_words:
                        truncated_content = " ".join(truncated_words) + "..."
                        compacted_parts.append(metadata + truncated_content)
                        current_tokens += metadata_tokens + word_count
                        break
        
        # Join all parts
        compacted_context = "\n\n".join(compacted_parts)
        
        logger.info(
            "Context compacted",
            original_docs=len(documents),
            final_tokens=current_tokens,
            max_tokens=self.max_tokens
        )
        
        return compacted_context
    
    def create_rag_prompt(self, query: str, contexts: List[Dict[str, Any]], system_prompt: str = "") -> str:
        """Create a RAG-enhanced prompt with compacted contexts"""
        # Compact contexts
        compacted_context = self.compact_by_token_limit(contexts, query)
        
        # Build prompt
        prompt_parts = []
        
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")
        
        prompt_parts.append("Context Information:")
        prompt_parts.append(compacted_context)
        prompt_parts.append("\n" + "="*50 + "\n")
        prompt_parts.append(f"User Query: {query}")
        prompt_parts.append("\nBased on the provided context, please answer the user's query.")
        
        full_prompt = "\n".join(prompt_parts)
        
        # Verify token limit
        total_tokens = self.count_tokens(full_prompt)
        if total_tokens > self.max_tokens:
            logger.warning(
                "Prompt exceeds token limit",
                total_tokens=total_tokens,
                max_tokens=self.max_tokens
            )
        
        return full_prompt
    
    def compact_memory_entries(self, memories: List[Dict[str, Any]], query: str) -> str:
        """Compact memory entries for memory retrieval"""
        if not memories:
            return "No relevant memories found."
        
        # Group memories by category
        by_category = {}
        for memory in memories:
            category = memory.get("category", "general")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(memory)
        
        # Build compacted memory string
        memory_parts = []
        
        for category, category_memories in by_category.items():
            if category_memories:
                memory_parts.append(f"\n{category.title()} Memories:")
                for memory in category_memories[:3]:  # Limit per category
                    content = memory.get("content", memory.get("value", ""))
                    timestamp = memory.get("timestamp", "")
                    
                    # Truncate if too long
                    if len(content) > 200:
                        content = content[:200] + "..."
                    
                    memory_parts.append(f"  • {content}")
        
        compacted_memories = "\n".join(memory_parts)
        
        logger.info(
            "Memories compacted",
            total_memories=len(memories),
            categories=len(by_category)
        )
        
        return compacted_memories

# Global compactor instance
_compactor = None

def get_compactor() -> ContextCompactor:
    """Get global compactor instance"""
    global _compactor
    if _compactor is None:
        _compactor = ContextCompactor()
    return _compactor

def reset_compactor():
    """Reset compactor instance (for testing)"""
    global _compactor
    _compactor = None