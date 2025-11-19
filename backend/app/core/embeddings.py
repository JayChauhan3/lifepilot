# Embeddings wrapper for multiple providers
import structlog
from typing import List, Union, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import os

logger = structlog.get_logger()

class EmbeddingProvider:
    """Base class for embedding providers"""
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        raise NotImplementedError

class SentenceTransformerProvider(EmbeddingProvider):
    """Sentence Transformers embedding provider"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info("Initializing SentenceTransformer", model=model_name)
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using SentenceTransformer"""
        logger.info("Generating embeddings", count=len(texts))
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()


class Embeddings:
    """Main embeddings wrapper with provider switching"""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider_name = provider or os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")
        self._provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the embedding provider"""
        if self.provider_name == "sentence-transformers":
            model_name = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
            self._provider = SentenceTransformerProvider(model_name)
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