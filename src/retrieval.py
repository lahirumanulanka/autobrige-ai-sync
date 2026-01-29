"""
Retrieval functions for strategy-action matching.
"""
from typing import List, Dict, Any, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from .models import StrategicObjective
    from .vector_store import ActionVectorStore


def get_strength_label(similarity: float) -> str:
    """
    Get strength label based on similarity score.
    
    Args:
        similarity: Similarity score (0-1)
        
    Returns:
        Strength label: "Strong", "Medium", or "Weak"
    """
    if similarity >= 0.75:
        return "Strong"
    elif similarity >= 0.55:
        return "Medium"
    else:
        return "Weak"


def retrieve_top_k_actions_for_strategy(
    strategy: "StrategicObjective",
    strategy_embedding: np.ndarray,
    store: "ActionVectorStore",
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k most similar actions for a strategy.
    
    Args:
        strategy: StrategicObjective instance
        strategy_embedding: Embedding vector for the strategy
        store: ActionVectorStore instance
        top_k: Number of top actions to retrieve
        
    Returns:
        List of dicts containing:
            - id: action ID
            - similarity: similarity score (0-1)
            - strength: strength label (Strong/Medium/Weak)
            - metadata: action metadata
            - document: action text
    """
    # Query vector store
    results = store.query_by_embedding(strategy_embedding, top_k=top_k)
    
    # Add strength labels
    for result in results:
        result['strength'] = get_strength_label(result['similarity'])
    
    return results
