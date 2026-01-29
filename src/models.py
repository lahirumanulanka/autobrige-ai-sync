"""
Pydantic models for strategic objectives and action tasks.
"""
import json
from typing import List, Optional
from pydantic import BaseModel, Field


class StrategicObjective(BaseModel):
    """Model for strategic objectives"""
    id: str
    title: str
    description: str
    kpis: List[str] = Field(default_factory=list)
    priority: str = "Medium"
    
    class Config:
        extra = "allow"


class ActionTask(BaseModel):
    """Model for action tasks"""
    id: str
    title: str
    description: str
    owner: str = "Unassigned"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    outputs: List[str] = Field(default_factory=list)
    
    class Config:
        extra = "allow"


def load_strategies(path: str) -> List[StrategicObjective]:
    """
    Load strategic objectives from a JSON file.
    
    Args:
        path: Path to JSON file containing array of strategies
        
    Returns:
        List of StrategicObjective instances
        
    Raises:
        ValueError: If JSON is not an array
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array in {path}, got {type(data).__name__}")
    
    return [StrategicObjective(**item) for item in data]


def load_actions(path: str) -> List[ActionTask]:
    """
    Load action tasks from a JSON file.
    
    Args:
        path: Path to JSON file containing array of actions
        
    Returns:
        List of ActionTask instances
        
    Raises:
        ValueError: If JSON is not an array
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array in {path}, got {type(data).__name__}")
    
    return [ActionTask(**item) for item in data]
