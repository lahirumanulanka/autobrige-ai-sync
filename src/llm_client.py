"""
LLM client for generating text using OpenAI API.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMUnavailableError(Exception):
    """Raised when LLM is not available (no API key)."""
    pass


def is_llm_available() -> bool:
    """
    Check if LLM is available (API key is set).
    
    Returns:
        True if OPENAI_API_KEY is set, False otherwise
    """
    api_key = os.getenv('OPENAI_API_KEY')
    return api_key is not None and api_key.strip() != '' and api_key != 'your_api_key_here'


def generate_text(system_prompt: str, user_prompt: str, model: str = "gpt-3.5-turbo") -> Optional[str]:
    """
    Generate text using OpenAI API.
    
    Args:
        system_prompt: System instructions for the model
        user_prompt: User query/prompt
        model: OpenAI model to use
        
    Returns:
        Generated text response or None if LLM unavailable
        
    Raises:
        LLMUnavailableError: If API key is not set
    """
    if not is_llm_available():
        raise LLMUnavailableError("OPENAI_API_KEY not found in environment variables")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            timeout=30.0
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        # Log error but don't crash
        print(f"Error generating text with LLM: {e}")
        raise LLMUnavailableError(f"Failed to generate text: {e}")
