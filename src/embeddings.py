"""
Embedding model wrapper using SentenceTransformers.
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict


class EmbeddingModel:
    """
    Wrapper for SentenceTransformer with caching and normalization.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model.
        
        Args:
            model_name: Name of the SentenceTransformer model
        """
        self.model = SentenceTransformer(model_name)
        self.cache: Dict[str, np.ndarray] = {}
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts with caching.
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of normalized embeddings (float32)
        """
        embeddings = []
        texts_to_encode = []
        indices_to_encode = []
        
        # Check cache first
        for i, text in enumerate(texts):
            if text in self.cache:
                embeddings.append(self.cache[text])
            else:
                texts_to_encode.append(text)
                indices_to_encode.append(i)
                embeddings.append(None)  # Placeholder
        
        # Encode uncached texts
        if texts_to_encode:
            new_embeddings = self.model.encode(
                texts_to_encode,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            ).astype(np.float32)
            
            # Update cache and embeddings list
            for idx, text, embedding in zip(indices_to_encode, texts_to_encode, new_embeddings):
                self.cache[text] = embedding
                embeddings[idx] = embedding
        
        # Stack into matrix
        embeddings_matrix = np.vstack(embeddings)
        return embeddings_matrix
    
    def embed_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text string
            
        Returns:
            Numpy array of normalized embedding (float32)
        """
        if text in self.cache:
            return self.cache[text]
        
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        ).astype(np.float32)
        
        self.cache[text] = embedding
        return embedding
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self.cache.clear()
