"""
Recommendations generator for strategy-action synchronization.
"""
from typing import List, Dict, Any
from .models import StrategicObjective
from .rag_engine import process_strategy_with_rag


def generate_recommendations(
    strategies: List[StrategicObjective],
    alignment_result: Dict[str, Any],
    rag_enabled: bool = True,
    threshold: float = 0.60
) -> List[Dict[str, Any]]:
    """
    Generate recommendations for strategies based on alignment results.
    
    Args:
        strategies: List of StrategicObjective instances
        alignment_result: Result from AlignmentEngine.compute_alignment()
        rag_enabled: Whether to enable RAG (LLM) generation
        threshold: Similarity threshold below which to generate detailed recommendations
        
    Returns:
        List of recommendation dictionaries, one per strategy
    """
    recommendations = []
    
    # Create a mapping of strategy_id to strategy object
    strategy_map = {s.id: s for s in strategies}
    
    # Process each strategy from alignment results
    for strategy_info in alignment_result['strategy_mapping']:
        strategy_id = strategy_info['strategy_id']
        strategy = strategy_map[strategy_id]
        avg_similarity = strategy_info['avg_top3_similarity']
        
        # Determine if detailed RAG processing is needed
        if avg_similarity < threshold:
            # Generate detailed recommendations using RAG
            recommendation = process_strategy_with_rag(
                strategy=strategy,
                alignment_info=strategy_info,
                rag_enabled=rag_enabled
            )
            recommendation['recommendation_type'] = 'detailed'
            recommendation['reason'] = f'Low alignment score ({avg_similarity:.3f}) below threshold ({threshold})'
        else:
            # Generate light suggestions without LLM call
            recommendation = {
                "strategy_id": strategy_id,
                "strategy_title": strategy_info['strategy_title'],
                "avg_similarity": round(avg_similarity, 3),
                "retrieved_actions": [
                    {
                        "id": action['id'],
                        "title": action['metadata']['title'],
                        "similarity": round(action['similarity'], 3),
                        "strength": action['strength']
                    }
                    for action in strategy_info['retrieved_actions'][:5]
                ],
                "augmented_prompt_preview": "N/A (alignment is sufficient)",
                "llm_enabled": False,
                "recommendation_type": "light",
                "reason": f'Good alignment score ({avg_similarity:.3f}) above threshold ({threshold})',
                "suggestions": [
                    f"Alignment for '{strategy_info['strategy_title']}' is satisfactory.",
                    "Continue monitoring action progress and maintain alignment.",
                    "Consider periodic reviews to ensure sustained alignment."
                ],
                "kpis": [
                    "Track action completion rates",
                    "Monitor alignment score trends"
                ],
                "risks": [
                    "Complacency due to good current alignment"
                ],
                "new_actions": []
            }
        
        recommendations.append(recommendation)
    
    return recommendations
