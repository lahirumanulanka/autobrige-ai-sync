"""
Text utilities for processing strategic objectives and action tasks.
"""

import re
from typing import Union
from src.models import StrategicObjective, ActionTask


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing.
    
    Args:
        text: Raw text string
        
    Returns:
        Cleaned text string
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def strategy_to_text(strategy: StrategicObjective) -> str:
    """
    Convert a strategic objective to a single text representation.
    
    Args:
        strategy: StrategicObjective instance
        
    Returns:
        Combined text representation for embedding
    """
    parts = []
    
    # Add title
    if strategy.title:
        parts.append(f"Title: {strategy.title}")
    
    # Add description
    if strategy.description:
        parts.append(f"Description: {strategy.description}")
    
    # Add KPIs
    if strategy.kpis:
        kpis_text = ", ".join(strategy.kpis)
        parts.append(f"KPIs: {kpis_text}")
    
    # Add priority
    if strategy.priority:
        parts.append(f"Priority: {strategy.priority}")
    
    # Combine all parts
    combined_text = " | ".join(parts)
    
    return clean_text(combined_text)


def action_to_text(action: ActionTask) -> str:
    """
    Convert an action task to a single text representation.
    
    Args:
        action: ActionTask instance
        
    Returns:
        Combined text representation for embedding
    """
    parts = []
    
    # Add title
    if action.title:
        parts.append(f"Title: {action.title}")
    
    # Add description
    if action.description:
        parts.append(f"Description: {action.description}")
    
    # Add outputs/deliverables
    if action.outputs:
        outputs_text = ", ".join(action.outputs)
        parts.append(f"Outputs: {outputs_text}")
    
    # Add owner
    if action.owner:
        parts.append(f"Owner: {action.owner}")
    
    # Combine all parts
    combined_text = " | ".join(parts)
    
    return clean_text(combined_text)
