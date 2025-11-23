# Embeddings wrapper for multiple providers
import structlog
from typing import List, Union, Optional
import numpy as np
import os
import google.generativeai as genai

logger = structlog.get_logger()

class EmbeddingProvider:
    """Base class for embedding providers"""
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        raise NotImplementedError


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Google Gemini embedding provider"""
    
    def __init__(self, model_name: str = "models/text-embedding-004"):
        logger.info("Initializing Gemini Embeddings", model=model_name)
        self.model_name = model_name
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not set")
            raise ValueError("GEMINI_API_KEY not set")
            
        genai.configure(api_key=api_key)
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Gemini"""
        logger.info("Generating Gemini embeddings", count=len(texts))
        try:
            # Gemini batch embedding
            result = genai.embed_content(
                model=self.model_name,
                content=texts,
                task_type="retrieval_document",
                title=None
            )
            
            if 'embedding' in result:
                embedding = result['embedding']
                # Check if it's already a list of lists (batch format) or single list (single format)
                if embedding and isinstance(embedding[0], list):
                    logger.info("Gemini returned batch format in 'embedding' field")
                    return embedding
                else:
                    logger.info("Gemini returned single format in 'embedding' field")
                    return [embedding]
            elif 'embeddings' in result:
                # Check if it's a list of lists or list of dicts
                first_item = result['embeddings'][0]
                logger.info("Embeddings list found", count=len(result['embeddings']), first_type=type(first_item))
                return result['embeddings']
            else:
                # Fallback or error
                logger.error("Unexpected Gemini embedding response format", result=str(result))
                return []
                
        except Exception as e:
            logger.error("Failed to generate Gemini embeddings", error=str(e))
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        # text-embedding-004 is 768 dimensions
        return 768


class Embeddings:
    """Main embeddings wrapper with provider switching"""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider_name = provider or os.getenv("EMBEDDING_PROVIDER", "gemini")
        self._provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the embedding provider"""
        if self.provider_name == "gemini":
            model_name = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
            self._provider = GeminiEmbeddingProvider(model_name)
        else:
            logger.error("Unknown embedding provider", provider=self.provider_name)
            raise ValueError(f"Unknown embedding provider: {self.provider_name}")
        
        logger.info("Embeddings initialized", provider=self.provider_name)
    
    def embed(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Generate embeddings for text(s)"""
        if isinstance(texts, str):
            texts = [texts]
        
        return self._provider.embed(texts)
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = self.embed([text])
        return embeddings[0]
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self._provider.get_dimension()
    
    def compute_similarity(self, query_embedding: List[float], doc_embeddings: List[List[float]]) -> List[float]:
        """Compute cosine similarity between query and documents"""
        query_np = np.array(query_embedding)
        doc_np = np.array(doc_embeddings)
        
        # Compute cosine similarity
        similarities = np.dot(doc_np, query_np) / (
            np.linalg.norm(doc_np, axis=1) * np.linalg.norm(query_np)
        )
        
        return similarities.tolist()
    
    def search_similar(self, query: str, doc_embeddings: List[List[float]], top_k: int = 5) -> List[tuple]:
        """Search for most similar documents"""
        query_embedding = self.embed_single(query)
        similarities = self.compute_similarity(query_embedding, doc_embeddings)
        
        # Get top-k results
        indexed_similarities = list(enumerate(similarities))
        indexed_similarities.sort(key=lambda x: x[1], reverse=True)
        
        return indexed_similarities[:top_k]

# Global embeddings instance
_embeddings = None

def get_embeddings() -> Embeddings:
    """Get global embeddings instance"""
    global _embeddings
    if _embeddings is None:
        _embeddings = Embeddings()
    return _embeddings

def reset_embeddings():
    """Reset embeddings instance (for testing)"""
    global _embeddings
    _embeddings = None