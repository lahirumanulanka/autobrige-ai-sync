"""
Pydantic models for Strategic Objectives and Action Tasks.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
import json


class StrategicObjective(BaseModel):
    """Model for a strategic objective."""
    id: str = Field(..., description="Unique identifier for the strategic objective")
    title: str = Field(..., description="Title of the strategic objective")
    description: str = Field(..., description="Detailed description of the objective")
    kpis: List[str] = Field(default_factory=list, description="Key Performance Indicators")
    priority: str = Field(default="Medium", description="Priority level (Low/Medium/High)")
    
    class Config:
        extra = "allow"


class ActionTask(BaseModel):
    """Model for an action task."""
    id: str = Field(..., description="Unique identifier for the action task")
    title: str = Field(..., description="Title of the action task")
    description: str = Field(..., description="Detailed description of the task")
    owner: str = Field(..., description="Person or team responsible for the task")
    start_date: Optional[str] = Field(None, description="Start date (ISO format)")
    end_date: Optional[str] = Field(None, description="End date (ISO format)")
    outputs: List[str] = Field(default_factory=list, description="Expected outputs/deliverables")
    
    class Config:
        extra = "allow"


def load_strategies(path: str) -> List[StrategicObjective]:
    """
    Load strategic objectives from a JSON file.
    
    Args:
        path: Path to the JSON file containing strategic objectives
        
    Returns:
        List of StrategicObjective instances
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "strategies" in data:
        data = data["strategies"]
    
    return [StrategicObjective(**item) for item in data]


def load_actions(path: str) -> List[ActionTask]:
    """
    Load action tasks from a JSON file.
    
    Args:
        path: Path to the JSON file containing action tasks
        
    Returns:
        List of ActionTask instances
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "actions" in data:
        data = data["actions"]
    
    return [ActionTask(**item) for item in data]
