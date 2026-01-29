"""
Text processing utilities for embeddings.
"""
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import StrategicObjective, ActionTask


def clean_text(text: str) -> str:
    """
    Clean and normalize text for embedding.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text with collapsed whitespace
    """
    # Strip leading/trailing whitespace
    text = text.strip()
    # Collapse multiple whitespace into single space
    text = re.sub(r'\s+', ' ', text)
    return text


def strategy_to_text(strategy: "StrategicObjective") -> str:
    """
    Convert strategic objective to deterministic text representation.
    
    Args:
        strategy: StrategicObjective instance
        
    Returns:
        Formatted text combining title, description, and KPIs
    """
    parts = [
        f"Title: {strategy.title}",
        f"Description: {strategy.description}"
    ]
    
    if strategy.kpis:
        kpis_text = ", ".join(strategy.kpis)
        parts.append(f"KPIs: {kpis_text}")
    
    text = " | ".join(parts)
    return clean_text(text)


def action_to_text(action: "ActionTask") -> str:
    """
    Convert action task to deterministic text representation.
    
    Args:
        action: ActionTask instance
        
    Returns:
        Formatted text combining title, description, owner, and outputs
    """
    parts = [
        f"Title: {action.title}",
        f"Description: {action.description}",
        f"Owner: {action.owner}"
    ]
    
    if action.outputs:
        outputs_text = ", ".join(action.outputs)
        parts.append(f"Outputs: {outputs_text}")
    
    text = " | ".join(parts)
    return clean_text(text)
