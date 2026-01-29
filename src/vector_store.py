"""
ChromaDB vector store for action tasks.
"""
import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Any


class ActionVectorStore:
    """
    Persistent ChromaDB vector store for action tasks.
    """
    
    def __init__(self, persist_directory: str = "chroma_db"):
        """
        Initialize persistent Chroma client.
        
        Args:
            persist_directory: Directory for persisting the database
        """
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "actions"
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get or create the actions collection with cosine similarity."""
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def reset(self):
        """Delete and recreate the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass  # Collection might not exist
        
        self.collection = self._get_or_create_collection()
    
    def upsert_actions(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict[str, Any]]
    ):
        """
        Insert or update actions in the vector store.
        
        Args:
            ids: List of action IDs
            documents: List of action text representations
            embeddings: Numpy array of embeddings
            metadatas: List of metadata dicts for each action
        """
        # Convert numpy array to list of lists
        embeddings_list = embeddings.tolist()
        
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadatas
        )
    
    def query_by_embedding(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query the vector store using an embedding.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of dicts with keys: id, similarity, metadata, document
        """
        # Convert numpy array to list
        query_embedding_list = query_embedding.tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding_list],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            # Convert cosine distance to similarity
            distance = results['distances'][0][i]
            similarity = 1.0 - distance
            
            formatted_results.append({
                'id': results['ids'][0][i],
                'similarity': similarity,
                'metadata': results['metadatas'][0][i],
                'document': results['documents'][0][i]
            })
        
        return formatted_results
    
    def count(self) -> int:
        """Get the number of items in the collection."""
        return self.collection.count()
