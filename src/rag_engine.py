"""
RAG engine for generating improvement suggestions.
"""
from typing import List, Dict, Any
from .models import StrategicObjective
from .rag_prompt import build_rag_prompt
from .llm_client import generate_text, is_llm_available, LLMUnavailableError


def generate_fallback_suggestions(
    strategy: StrategicObjective,
    avg_similarity: float,
    retrieved_actions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate rule-based fallback suggestions when LLM is unavailable.
    
    Args:
        strategy: StrategicObjective instance
        avg_similarity: Average similarity score
        retrieved_actions: List of retrieved action dicts
        
    Returns:
        Structured suggestions dictionary
    """
    strength = "Strong" if avg_similarity >= 0.75 else "Medium" if avg_similarity >= 0.55 else "Weak"
    
    # Generate suggestions based on alignment strength
    if avg_similarity < 0.55:
        suggestions = [
            f"The alignment for '{strategy.title}' is currently weak (score: {avg_similarity:.2f}). Consider creating more specific action tasks that directly address this strategic objective.",
            "Review the existing actions to ensure they explicitly contribute to this strategy's goals.",
            "Establish clear KPIs that can measure progress toward this strategic objective.",
            "Schedule regular reviews to assess whether actions are effectively supporting this strategy."
        ]
    elif avg_similarity < 0.75:
        suggestions = [
            f"The alignment for '{strategy.title}' is moderate (score: {avg_similarity:.2f}). Some actions are aligned, but there's room for improvement.",
            "Consider enhancing the specificity of action descriptions to better reflect strategic intent.",
            "Add more action tasks that directly target key aspects of this strategic objective.",
            "Strengthen connections between existing actions and strategic KPIs."
        ]
    else:
        suggestions = [
            f"The alignment for '{strategy.title}' is strong (score: {avg_similarity:.2f}). Actions are well-aligned with this strategy.",
            "Continue monitoring action progress to ensure sustained alignment.",
            "Consider optimizing resource allocation across the well-aligned actions.",
            "Document best practices from this strategy to apply to others with weaker alignment."
        ]
    
    # Generate new action proposals
    new_actions = [
        {
            "title": f"Review and update {strategy.title} implementation plan",
            "description": f"Conduct quarterly review of actions supporting {strategy.title} to ensure continued alignment and effectiveness",
            "owner": "Strategy Team",
            "timeline": "Q1-Q4 (Recurring)"
        },
        {
            "title": f"KPI tracking for {strategy.title}",
            "description": f"Establish dashboard and tracking mechanisms for measuring progress on {strategy.title}",
            "owner": "Analytics Team",
            "timeline": "Q1 2024"
        }
    ]
    
    # Generate KPIs
    kpis = [
        f"Number of actions aligned with {strategy.title} (target: >5 with strong alignment)",
        f"Average alignment score for {strategy.title} (target: >0.75)",
        "Percentage of actions completed on time"
    ]
    
    # Identify risks
    risks = [
        f"Current alignment score of {avg_similarity:.2f} may indicate insufficient action coverage",
        "Resource constraints might limit execution of supporting actions",
        "Lack of clear ownership for some related actions"
    ]
    
    return {
        "suggestions": suggestions,
        "new_actions": new_actions,
        "kpis": kpis,
        "risks": risks
    }


def generate_rag_suggestions(
    strategy: StrategicObjective,
    avg_similarity: float,
    retrieved_actions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate suggestions using RAG (LLM-based).
    
    Args:
        strategy: StrategicObjective instance
        avg_similarity: Average similarity score
        retrieved_actions: List of retrieved action dicts
        
    Returns:
        Structured suggestions dictionary
    """
    # Build augmented prompt
    prompt_data = build_rag_prompt(strategy, avg_similarity, retrieved_actions)
    
    try:
        # Generate text using LLM
        llm_response = generate_text(
            system_prompt=prompt_data['system_prompt'],
            user_prompt=prompt_data['user_prompt']
        )
        
        # Parse LLM response (simplified - in production, use more robust parsing)
        # For now, return structured output with LLM text
        return {
            "suggestions": [
                "LLM-generated suggestion (parsing not fully implemented in this version)",
                llm_response[:500] if llm_response else "No response generated"
            ],
            "new_actions": [
                {
                    "title": "LLM-suggested action",
                    "description": "Parse from LLM response",
                    "owner": "TBD",
                    "timeline": "TBD"
                }
            ],
            "kpis": ["Parse KPIs from LLM response"],
            "risks": ["Parse risks from LLM response"],
            "llm_raw_response": llm_response
        }
    
    except LLMUnavailableError:
        # Fall back to rule-based suggestions
        return generate_fallback_suggestions(strategy, avg_similarity, retrieved_actions)


def process_strategy_with_rag(
    strategy: StrategicObjective,
    alignment_info: Dict[str, Any],
    rag_enabled: bool = True
) -> Dict[str, Any]:
    """
    Process a single strategy through the RAG pipeline.
    
    Args:
        strategy: StrategicObjective instance
        alignment_info: Alignment information for this strategy
        rag_enabled: Whether to use LLM (True) or fallback mode (False)
        
    Returns:
        Dictionary containing:
            - strategy_id, strategy_title
            - avg_similarity
            - retrieved_actions (summary)
            - augmented_prompt_preview
            - llm_enabled
            - suggestions, kpis, risks, new_actions
    """
    avg_similarity = alignment_info['avg_top3_similarity']
    retrieved_actions = alignment_info['retrieved_actions']
    
    # Build prompt for context
    prompt_data = build_rag_prompt(strategy, avg_similarity, retrieved_actions)
    
    # Determine if LLM should be used
    llm_available = is_llm_available() and rag_enabled
    
    # Generate suggestions
    if llm_available:
        suggestion_data = generate_rag_suggestions(strategy, avg_similarity, retrieved_actions)
    else:
        suggestion_data = generate_fallback_suggestions(strategy, avg_similarity, retrieved_actions)
    
    # Build output
    return {
        "strategy_id": strategy.id,
        "strategy_title": strategy.title,
        "avg_similarity": round(avg_similarity, 3),
        "retrieved_actions": [
            {
                "id": action['id'],
                "title": action['metadata']['title'],
                "similarity": round(action['similarity'], 3),
                "strength": action['strength']
            }
            for action in retrieved_actions[:5]
        ],
        "augmented_prompt_preview": prompt_data['context_block'][:300] + "...",
        "llm_enabled": llm_available,
        "suggestions": suggestion_data['suggestions'],
        "kpis": suggestion_data['kpis'],
        "risks": suggestion_data['risks'],
        "new_actions": suggestion_data['new_actions']
    }
