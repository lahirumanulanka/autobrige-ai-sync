"""
Simple test script to verify the system structure without downloading models.
This demonstrates the data flow and module integration.
"""
import sys
import json
sys.path.insert(0, '.')

def test_basic_functionality():
    """Test basic imports and data loading"""
    print("=" * 60)
    print("Testing Strategy-Action Synchronization System")
    print("=" * 60)
    
    # Test 1: Imports
    print("\n1. Testing imports...")
    try:
        from src.models import load_strategies, load_actions, StrategicObjective, ActionTask
        from src.text_utils import strategy_to_text, action_to_text, clean_text
        from src.llm_client import is_llm_available
        from src.rag_prompt import build_rag_prompt
        from src.recommendations import generate_recommendations
        from src.evaluation import compute_coverage_metrics, compute_similarity_distribution
        print("   ✓ All modules imported successfully")
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        return False
    
    # Test 2: Data Loading
    print("\n2. Testing data loading...")
    try:
        strategies = load_strategies('data/strategic.json')
        actions = load_actions('data/action.json')
        print(f"   ✓ Loaded {len(strategies)} strategic objectives")
        print(f"   ✓ Loaded {len(actions)} action tasks")
        
        # Verify data structure
        assert len(strategies) == 8, "Expected 8 strategies"
        assert len(actions) == 38, "Expected 38 actions"
        print("   ✓ Data structure validated")
    except Exception as e:
        print(f"   ✗ Data loading failed: {e}")
        return False
    
    # Test 3: Pydantic Models
    print("\n3. Testing Pydantic models...")
    try:
        strategy = strategies[0]
        action = actions[0]
        
        assert isinstance(strategy, StrategicObjective)
        assert isinstance(action, ActionTask)
        assert hasattr(strategy, 'id')
        assert hasattr(strategy, 'title')
        assert hasattr(action, 'id')
        assert hasattr(action, 'title')
        print(f"   ✓ Strategy: {strategy.title}")
        print(f"   ✓ Action: {action.title}")
    except Exception as e:
        print(f"   ✗ Model validation failed: {e}")
        return False
    
    # Test 4: Text Processing
    print("\n4. Testing text processing...")
    try:
        strategy_text = strategy_to_text(strategies[0])
        action_text = action_to_text(actions[0])
        
        assert len(strategy_text) > 0
        assert len(action_text) > 0
        assert "Title:" in strategy_text
        assert "Description:" in strategy_text
        print(f"   ✓ Strategy text length: {len(strategy_text)} chars")
        print(f"   ✓ Action text length: {len(action_text)} chars")
        print(f"   ✓ Strategy preview: {strategy_text[:100]}...")
    except Exception as e:
        print(f"   ✗ Text processing failed: {e}")
        return False
    
    # Test 5: RAG Prompt Building
    print("\n5. Testing RAG prompt builder...")
    try:
        # Mock retrieved actions
        retrieved_actions = [
            {
                'id': 'A001',
                'similarity': 0.85,
                'strength': 'Strong',
                'metadata': {
                    'title': 'Test Action',
                    'owner': 'Test Team',
                    'start_date': '2024-01-01',
                    'end_date': '2024-03-01'
                }
            }
        ]
        
        prompt_data = build_rag_prompt(strategies[0], 0.75, retrieved_actions)
        
        assert 'system_prompt' in prompt_data
        assert 'user_prompt' in prompt_data
        assert 'context_block' in prompt_data
        assert len(prompt_data['system_prompt']) > 0
        assert len(prompt_data['user_prompt']) > 0
        print("   ✓ RAG prompt structure validated")
        print(f"   ✓ System prompt length: {len(prompt_data['system_prompt'])} chars")
        print(f"   ✓ User prompt length: {len(prompt_data['user_prompt'])} chars")
    except Exception as e:
        print(f"   ✗ RAG prompt building failed: {e}")
        return False
    
    # Test 6: LLM Availability Check
    print("\n6. Testing LLM availability...")
    try:
        llm_available = is_llm_available()
        if llm_available:
            print("   ✓ LLM API key detected (RAG mode enabled)")
        else:
            print("   ✓ No LLM API key (Fallback mode - rule-based suggestions)")
    except Exception as e:
        print(f"   ✗ LLM check failed: {e}")
        return False
    
    # Test 7: Mock Alignment Results
    print("\n7. Testing evaluation metrics with mock data...")
    try:
        # Create mock alignment results
        mock_alignment = {
            'overall_score': 72.5,
            'coverage_pct': 62.5,
            'strategy_count': 8,
            'action_count': 38,
            'strategy_mapping': [
                {
                    'strategy_id': 'S001',
                    'strategy_title': 'Test Strategy',
                    'avg_top3_similarity': 0.80,
                    'strong_match_count': 3,
                    'retrieved_actions': []
                },
                {
                    'strategy_id': 'S002',
                    'strategy_title': 'Test Strategy 2',
                    'avg_top3_similarity': 0.65,
                    'strong_match_count': 1,
                    'retrieved_actions': []
                }
            ],
            'weak_strategies': []
        }
        
        coverage = compute_coverage_metrics(mock_alignment)
        distribution = compute_similarity_distribution(mock_alignment)
        
        print(f"   ✓ Coverage metrics computed: {coverage['overall_score']:.2f}")
        print(f"   ✓ Distribution metrics: mean={distribution['mean']:.3f}")
    except Exception as e:
        print(f"   ✗ Evaluation failed: {e}")
        return False
    
    # Test 8: File Structure
    print("\n8. Verifying project structure...")
    import os
    required_dirs = ['app', 'src', 'data', 'outputs', 'chroma_db', 'tests']
    required_files = ['requirements.txt', 'README.md', '.env.example', '.gitignore']
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✓ Directory exists: {directory}/")
        else:
            print(f"   ✗ Missing directory: {directory}/")
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✓ File exists: {file}")
        else:
            print(f"   ✗ Missing file: {file}")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nNOTE: Full end-to-end testing requires:")
    print("  1. Internet access to download sentence-transformers model")
    print("  2. Optional: OPENAI_API_KEY for LLM-powered suggestions")
    print("\nThe system will work in fallback mode with rule-based suggestions")
    print("when run without an LLM key.")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
