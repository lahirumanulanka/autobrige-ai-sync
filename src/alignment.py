"""
Alignment engine for strategy-action synchronization.
"""
from typing import List, Dict, Any
from .models import StrategicObjective, ActionTask
from .text_utils import strategy_to_text, action_to_text
from .embeddings import EmbeddingModel
from .vector_store import ActionVectorStore
from .retrieval import retrieve_top_k_actions_for_strategy


class AlignmentEngine:
    """
    Engine for computing strategy-action alignment and synchronization scores.
    """
    
    def __init__(
        self,
        strategies: List[StrategicObjective],
        actions: List[ActionTask],
        embedding_model: EmbeddingModel = None,
        vector_store: ActionVectorStore = None,
        persist_directory: str = "chroma_db"
    ):
        """
        Initialize alignment engine.
        
        Args:
            strategies: List of strategic objectives
            actions: List of action tasks
            embedding_model: EmbeddingModel instance (creates default if None)
            vector_store: ActionVectorStore instance (creates default if None)
            persist_directory: Directory for ChromaDB persistence
        """
        self.strategies = strategies
        self.actions = actions
        self.embedding_model = embedding_model or EmbeddingModel()
        self.vector_store = vector_store or ActionVectorStore(persist_directory)
    
    def index_actions(self):
        """Index all actions in the vector store."""
        # Reset the collection
        self.vector_store.reset()
        
        # Generate action texts and embeddings
        action_texts = [action_to_text(action) for action in self.actions]
        action_embeddings = self.embedding_model.embed_texts(action_texts)
        
        # Prepare metadata
        action_ids = [action.id for action in self.actions]
        action_metadatas = [
            {
                'title': action.title,
                'owner': action.owner,
                'start_date': action.start_date or '',
                'end_date': action.end_date or ''
            }
            for action in self.actions
        ]
        
        # Upsert into vector store
        self.vector_store.upsert_actions(
            ids=action_ids,
            documents=action_texts,
            embeddings=action_embeddings,
            metadatas=action_metadatas
        )
    
    def compute_alignment(self, top_k: int = 5) -> Dict[str, Any]:
        """
        Compute alignment between strategies and actions.
        
        Args:
            top_k: Number of top actions to retrieve per strategy
            
        Returns:
            Dictionary containing:
                - overall_score: Overall synchronization score (0-100)
                - coverage_pct: Percentage of strategies with >=2 Strong matches
                - strategy_count: Number of strategies
                - action_count: Number of actions
                - strategy_mapping: Per-strategy mapping details
                - weak_strategies: List of strategies with avg_top3_similarity < 0.55
        """
        # Index actions first
        self.index_actions()
        
        strategy_mappings = []
        avg_similarities = []
        strong_coverage_count = 0
        weak_strategies = []
        
        for strategy in self.strategies:
            # Generate strategy text and embedding
            strategy_text = strategy_to_text(strategy)
            strategy_embedding = self.embedding_model.embed_single(strategy_text)
            
            # Retrieve top-k actions
            retrieved_actions = retrieve_top_k_actions_for_strategy(
                strategy=strategy,
                strategy_embedding=strategy_embedding,
                store=self.vector_store,
                top_k=top_k
            )
            
            # Compute avg_top3_similarity
            top3_similarities = [r['similarity'] for r in retrieved_actions[:3]]
            avg_top3_similarity = sum(top3_similarities) / len(top3_similarities) if top3_similarities else 0.0
            avg_similarities.append(avg_top3_similarity)
            
            # Count strong matches
            strong_matches = [r for r in retrieved_actions if r['strength'] == 'Strong']
            if len(strong_matches) >= 2:
                strong_coverage_count += 1
            
            # Track weak strategies
            if avg_top3_similarity < 0.55:
                weak_strategies.append({
                    'id': strategy.id,
                    'title': strategy.title,
                    'avg_top3_similarity': avg_top3_similarity
                })
            
            # Build strategy mapping
            strategy_mappings.append({
                'strategy_id': strategy.id,
                'strategy_title': strategy.title,
                'strategy_text': strategy_text,
                'avg_top3_similarity': avg_top3_similarity,
                'retrieved_actions': retrieved_actions,
                'strong_match_count': len(strong_matches)
            })
        
        # Compute overall metrics
        overall_score = (sum(avg_similarities) / len(avg_similarities) * 100) if avg_similarities else 0.0
        coverage_pct = (strong_coverage_count / len(self.strategies) * 100) if self.strategies else 0.0
        
        return {
            'overall_score': round(overall_score, 2),
            'coverage_pct': round(coverage_pct, 2),
            'strategy_count': len(self.strategies),
            'action_count': len(self.actions),
            'strategy_mapping': strategy_mappings,
            'weak_strategies': weak_strategies
        }
