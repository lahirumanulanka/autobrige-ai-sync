"""
Vector store implementation using ChromaDB for storing and querying action embeddings.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Tuple
import numpy as np


class VectorStore:
    """
    Manages the ChromaDB vector database for action embeddings.
    """
    
    def __init__(self, persist_directory: str = "chroma_db"):
        """
        Initialize the ChromaDB client with persistent storage.
        
        Args:
            persist_directory: Directory path for persistent storage
        """
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            is_persistent=True
        ))
        
        # Get or create the actions collection
        self.collection = self.client.get_or_create_collection(
            name="actions",
            metadata={"description": "Action task embeddings"}
        )
    
    def upsert_actions(
        self,
        action_ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ):
        """
        Upsert action embeddings into the vector store.
        
        Args:
            action_ids: List of action IDs
            embeddings: List of embedding vectors
            documents: List of document texts
            metadata: List of metadata dictionaries (title, owner, dates)
        """
        self.collection.upsert(
            ids=action_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadata
        )
    
    def query_by_embedding(
        self,
        embedding: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query the vector store by embedding to find similar actions.
        
        Args:
            embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing action id, similarity score, and metadata
        """
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        
        # Parse results
        formatted_results = []
        
        if results and results['ids'] and len(results['ids']) > 0:
            ids = results['ids'][0]
            distances = results['distances'][0]
            metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(ids)
            documents = results['documents'][0] if results['documents'] else [''] * len(ids)
            
            for i in range(len(ids)):
                # ChromaDB returns cosine distance (lower is more similar)
                # Convert to similarity score (higher is more similar)
                cosine_distance = distances[i]
                similarity_score = 1 - cosine_distance
                
                formatted_results.append({
                    'id': ids[i],
                    'similarity_score': float(similarity_score),
                    'metadata': metadatas[i],
                    'document': documents[i]
                })
        
        return formatted_results
    
    def clear_collection(self):
        """Clear all items from the actions collection."""
        # Delete and recreate the collection
        self.client.delete_collection(name="actions")
        self.collection = self.client.get_or_create_collection(
            name="actions",
            metadata={"description": "Action task embeddings"}
        )
