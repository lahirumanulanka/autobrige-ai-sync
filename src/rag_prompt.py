"""
RAG prompt builder for generating improvement suggestions.
"""
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import StrategicObjective


def build_rag_prompt(
    strategy: "StrategicObjective",
    avg_similarity: float,
    retrieved_actions: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Build augmented prompt for RAG-based suggestion generation.
    
    Args:
        strategy: StrategicObjective instance
        avg_similarity: Average similarity score
        retrieved_actions: List of retrieved action dicts
        
    Returns:
        Dictionary containing:
            - system_prompt: Instructions for the LLM
            - user_prompt: User query with context
            - context_block: The grounded context data
    """
    # Build context block
    context_parts = []
    context_parts.append("=== STRATEGIC OBJECTIVE ===")
    context_parts.append(f"ID: {strategy.id}")
    context_parts.append(f"Title: {strategy.title}")
    context_parts.append(f"Description: {strategy.description}")
    context_parts.append(f"Priority: {strategy.priority}")
    
    if strategy.kpis:
        context_parts.append(f"KPIs: {', '.join(strategy.kpis)}")
    
    context_parts.append(f"\nCurrent Alignment Score: {avg_similarity:.3f}")
    context_parts.append(f"Alignment Status: {'Strong' if avg_similarity >= 0.75 else 'Medium' if avg_similarity >= 0.55 else 'Weak'}")
    
    context_parts.append("\n=== RETRIEVED ACTIONS (Most Similar) ===")
    for i, action in enumerate(retrieved_actions, 1):
        context_parts.append(f"\nAction {i}:")
        context_parts.append(f"  ID: {action['id']}")
        context_parts.append(f"  Title: {action['metadata']['title']}")
        context_parts.append(f"  Similarity: {action['similarity']:.3f} ({action['strength']})")
        context_parts.append(f"  Owner: {action['metadata']['owner']}")
        if action['metadata'].get('start_date'):
            context_parts.append(f"  Timeline: {action['metadata']['start_date']} to {action['metadata']['end_date']}")
    
    context_block = "\n".join(context_parts)
    
    # Build system prompt
    system_prompt = """You are an expert business strategy consultant specializing in action planning and strategic alignment.

Your task is to analyze the alignment between a strategic objective and its related action tasks, then provide actionable recommendations to improve synchronization.

IMPORTANT RULES:
1. Base your analysis ONLY on the provided context (strategy and retrieved actions)
2. Do not hallucinate or invent information not present in the context
3. Make reasonable business assumptions where needed, but clearly state them
4. Provide specific, actionable suggestions with clear implementation steps
5. Structure your response professionally for business stakeholders
6. Focus on improving alignment and achieving strategic goals"""

    # Build user prompt
    user_prompt = f"""Given the following context, analyze the alignment between this strategic objective and its related actions.

{context_block}

Based on this context, please provide:

1. **Improvement Suggestions**: 3-5 specific, actionable recommendations to strengthen alignment between this strategy and actions. Each suggestion should be concrete and implementable.

2. **New Action Proposals**: 2-3 new action tasks that could be created to better support this strategic objective. For each action, provide:
   - Title
   - Description
   - Suggested owner/department
   - Estimated timeline

3. **Key Performance Indicators**: 2-3 measurable KPIs to track progress toward this strategic objective.

4. **Risk Assessment**: 2-3 key risks or challenges that might prevent achieving this strategic objective, based on the current action portfolio.

Format your response in a clear, structured manner suitable for JSON parsing."""

    return {
        'system_prompt': system_prompt,
        'user_prompt': user_prompt,
        'context_block': context_block
    }
