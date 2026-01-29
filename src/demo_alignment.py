"""
Demo alignment engine that works without internet connection.
Uses random embeddings for testing the UI.
"""

from typing import List, Dict, Any
import numpy as np
import random

from src.models import StrategicObjective, ActionTask
from src.text_utils import strategy_to_text, action_to_text


class DemoAlignmentEngine:
    """
    Demo engine for testing without internet connection.
    Uses random embeddings instead of real sentence transformers.
    """
    
    def __init__(self, model_name: str = "demo", persist_directory: str = "chroma_db"):
        """Initialize demo engine."""
        self.model_name = model_name
        random.seed(42)  # For reproducible results
        np.random.seed(42)
    
    def _generate_mock_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate random embeddings for demo purposes."""
        # Create embeddings with some correlation based on text similarity
        embeddings = []
        for text in texts:
            # Use hash of text to create consistent embeddings
            text_hash = hash(text) % 1000
            base = np.random.RandomState(text_hash).randn(384)
            embeddings.append(base / np.linalg.norm(base))
        return np.array(embeddings)
    
    def _classify_alignment(self, score: float) -> str:
        """Classify alignment strength."""
        if score >= 0.6:
            return "Strong"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Weak"
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def analyze_alignment(
        self,
        strategies: List[StrategicObjective],
        actions: List[ActionTask],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze alignment between strategies and actions (demo version).
        """
        # Convert to text
        strategy_texts = [strategy_to_text(s) for s in strategies]
        action_texts = [action_to_text(a) for a in actions]
        
        # Generate mock embeddings
        strategy_embeddings = self._generate_mock_embeddings(strategy_texts)
        action_embeddings = self._generate_mock_embeddings(action_texts)
        
        # Analyze each strategy
        strategy_results = []
        strategy_scores = []
        strong_alignments_count = []
        
        for i, strategy in enumerate(strategies):
            strategy_embedding = strategy_embeddings[i]
            
            # Calculate similarity with all actions
            similarities = []
            for j, action in enumerate(actions):
                action_embedding = action_embeddings[j]
                similarity = self._cosine_similarity(strategy_embedding, action_embedding)
                
                # Add some domain knowledge boost for keyword matching
                strategy_lower = strategy_texts[i].lower()
                action_lower = action_texts[j].lower()
                
                # Boost similarity if they share important keywords
                keywords_map = {
                    'cost': ['cost', 'fee', 'price', 'pricing', 'calculator', 'financial'],
                    'transparency': ['transparency', 'clear', 'documentation', 'guide'],
                    'customer': ['customer', 'client', 'satisfaction', 'feedback', 'survey', 'support'],
                    'trust': ['trust', 'engagement', 'retention', 'communication', 'forum'],
                    'onboarding': ['onboarding', 'onboard', 'welcome', 'tutorial', 'workflow', 'verification'],
                    'auction': ['auction', 'bid', 'bidding', 'strategy'],
                    'analytics': ['analytics', 'data', 'dashboard', 'report', 'insight', 'analysis'],
                    'importer': ['importer', 'import', 'importing']
                }
                
                # Calculate keyword overlap
                keyword_boost = 0.0
                for main_kw, related_kws in keywords_map.items():
                    strategy_has = any(kw in strategy_lower for kw in related_kws)
                    action_has = any(kw in action_lower for kw in related_kws)
                    if strategy_has and action_has:
                        keyword_boost += 0.15  # Significant boost for shared concept
                
                similarity += keyword_boost
                similarity = min(similarity, 0.95)  # Cap at 0.95 for realism
                
                similarities.append({
                    'action_idx': j,
                    'action': action,
                    'similarity': similarity
                })
            
            # Sort by similarity and get top K
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            top_matches = similarities[:top_k]
            
            # Build results
            matches = []
            top_3_scores = []
            strong_count = 0
            
            for match in top_matches:
                score = match['similarity']
                action = match['action']
                alignment = self._classify_alignment(score)
                
                if alignment == "Strong":
                    strong_count += 1
                
                matches.append({
                    'action_id': action.id,
                    'action_title': action.title,
                    'similarity_score': round(float(score), 4),
                    'alignment': alignment
                })
                
                if len(top_3_scores) < 3:
                    top_3_scores.append(score)
            
            # Calculate strategy average
            strategy_avg_score = np.mean(top_3_scores) if top_3_scores else 0.0
            strategy_scores.append(strategy_avg_score)
            strong_alignments_count.append(strong_count)
            
            strategy_results.append({
                'strategy_id': strategy.id,
                'strategy_title': strategy.title,
                'strategy_priority': strategy.priority,
                'average_score': round(float(strategy_avg_score), 4),
                'alignment_level': self._classify_alignment(strategy_avg_score),
                'matching_actions': matches
            })
        
        # Compute overall metrics
        overall_score = np.mean(strategy_scores) * 100 if strategy_scores else 0.0
        
        # Calculate coverage
        strategies_with_good_coverage = sum(1 for count in strong_alignments_count if count >= 2)
        coverage_percentage = (strategies_with_good_coverage / len(strategies) * 100) if strategies else 0.0
        
        return {
            'overall_synchronization_score': round(float(overall_score), 2),
            'coverage_percentage': round(float(coverage_percentage), 2),
            'total_strategies': len(strategies),
            'total_actions': len(actions),
            'strategy_alignments': strategy_results
        }
