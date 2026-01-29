"""
Alignment engine for computing synchronization between strategies and actions.
"""

from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np

from src.models import StrategicObjective, ActionTask
from src.text_utils import strategy_to_text, action_to_text
from src.vector_store import VectorStore


class AlignmentEngine:
    """
    Engine for computing alignment between strategic objectives and action tasks.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        persist_directory: str = "chroma_db"
    ):
        """
        Initialize the alignment engine.
        
        Args:
            model_name: Name of the sentence transformer model
            persist_directory: Directory for ChromaDB persistence
        """
        self.model = SentenceTransformer(model_name)
        self.vector_store = VectorStore(persist_directory=persist_directory)
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def _classify_alignment(self, score: float) -> str:
        """
        Classify alignment strength based on similarity score.
        
        Args:
            score: Similarity score (0-1)
            
        Returns:
            Classification label: "Strong", "Medium", or "Weak"
        """
        if score >= 0.6:
            return "Strong"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Weak"
    
    def analyze_alignment(
        self,
        strategies: List[StrategicObjective],
        actions: List[ActionTask],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze alignment between strategies and actions.
        
        Args:
            strategies: List of strategic objectives
            actions: List of action tasks
            top_k: Number of top matching actions to consider per strategy
            
        Returns:
            Dictionary containing alignment results
        """
        # Convert actions to text
        action_texts = [action_to_text(action) for action in actions]
        action_ids = [action.id for action in actions]
        
        # Generate action embeddings
        action_embeddings = self._generate_embeddings(action_texts)
        
        # Prepare action metadata
        action_metadata = []
        for action in actions:
            metadata = {
                'title': action.title,
                'owner': action.owner,
                'start_date': action.start_date or '',
                'end_date': action.end_date or ''
            }
            action_metadata.append(metadata)
        
        # Index actions in vector store
        self.vector_store.clear_collection()
        self.vector_store.upsert_actions(
            action_ids=action_ids,
            embeddings=action_embeddings,
            documents=action_texts,
            metadata=action_metadata
        )
        
        # Analyze each strategy
        strategy_results = []
        strategy_scores = []
        strong_alignments_count = []
        
        for strategy in strategies:
            strategy_text = strategy_to_text(strategy)
            strategy_embedding = self._generate_embeddings([strategy_text])[0]
            
            # Query for matching actions
            matching_actions = self.vector_store.query_by_embedding(
                embedding=strategy_embedding,
                top_k=top_k
            )
            
            # Calculate strategy alignment
            matches = []
            top_3_scores = []
            strong_count = 0
            
            for match in matching_actions:
                score = match['similarity_score']
                alignment = self._classify_alignment(score)
                
                if alignment == "Strong":
                    strong_count += 1
                
                matches.append({
                    'action_id': match['id'],
                    'action_title': match['metadata'].get('title', ''),
                    'similarity_score': round(score, 4),
                    'alignment': alignment
                })
                
                # Track top 3 scores for strategy average
                if len(top_3_scores) < 3:
                    top_3_scores.append(score)
            
            # Calculate strategy average (top 3)
            strategy_avg_score = np.mean(top_3_scores) if top_3_scores else 0.0
            strategy_scores.append(strategy_avg_score)
            strong_alignments_count.append(strong_count)
            
            strategy_results.append({
                'strategy_id': strategy.id,
                'strategy_title': strategy.title,
                'strategy_priority': strategy.priority,
                'average_score': round(strategy_avg_score, 4),
                'alignment_level': self._classify_alignment(strategy_avg_score),
                'matching_actions': matches
            })
        
        # Compute overall metrics
        overall_score = np.mean(strategy_scores) * 100 if strategy_scores else 0.0
        
        # Calculate coverage percentage (strategies with >=2 strong actions)
        strategies_with_good_coverage = sum(1 for count in strong_alignments_count if count >= 2)
        coverage_percentage = (strategies_with_good_coverage / len(strategies) * 100) if strategies else 0.0
        
        return {
            'overall_synchronization_score': round(overall_score, 2),
            'coverage_percentage': round(coverage_percentage, 2),
            'total_strategies': len(strategies),
            'total_actions': len(actions),
            'strategy_alignments': strategy_results
        }
