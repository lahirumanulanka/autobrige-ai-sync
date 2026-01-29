"""
Test script for Strategy-Action Synchronization AI System
Run this to verify all modules work correctly.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_data_loading():
    """Test data loading functionality."""
    print("=" * 60)
    print("TEST 1: Data Loading")
    print("=" * 60)
    
    try:
        from src.models import load_strategies, load_actions
        
        strategies = load_strategies('data/strategic.json')
        actions = load_actions('data/action.json')
        
        print(f"✅ Loaded {len(strategies)} strategies")
        print(f"✅ Loaded {len(actions)} actions")
        
        # Verify data structure
        assert len(strategies) > 0, "No strategies loaded"
        assert len(actions) > 0, "No actions loaded"
        
        # Check first strategy
        s = strategies[0]
        print(f"\n📋 Sample Strategy:")
        print(f"   ID: {s.id}")
        print(f"   Title: {s.title}")
        print(f"   Priority: {s.priority}")
        print(f"   KPIs: {len(s.kpis)}")
        
        # Check first action
        a = actions[0]
        print(f"\n📋 Sample Action:")
        print(f"   ID: {a.id}")
        print(f"   Title: {a.title}")
        print(f"   Owner: {a.owner}")
        print(f"   Outputs: {len(a.outputs)}")
        
        print("\n✅ Data loading test PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Data loading test FAILED: {e}\n")
        return False


def test_text_processing():
    """Test text processing utilities."""
    print("=" * 60)
    print("TEST 2: Text Processing")
    print("=" * 60)
    
    try:
        from src.models import load_strategies, load_actions
        from src.text_utils import strategy_to_text, action_to_text, clean_text
        
        strategies = load_strategies('data/strategic.json')
        actions = load_actions('data/action.json')
        
        # Test strategy to text
        s_text = strategy_to_text(strategies[0])
        print(f"✅ Strategy text conversion:")
        print(f"   Length: {len(s_text)} characters")
        print(f"   Preview: {s_text[:150]}...")
        
        # Test action to text
        a_text = action_to_text(actions[0])
        print(f"\n✅ Action text conversion:")
        print(f"   Length: {len(a_text)} characters")
        print(f"   Preview: {a_text[:150]}...")
        
        # Test clean text
        dirty_text = "  This   has   extra    spaces  "
        clean = clean_text(dirty_text)
        print(f"\n✅ Text cleaning:")
        print(f"   Before: '{dirty_text}'")
        print(f"   After: '{clean}'")
        
        assert len(s_text) > 0, "Strategy text is empty"
        assert len(a_text) > 0, "Action text is empty"
        assert "  " not in clean, "Text cleaning failed"
        
        print("\n✅ Text processing test PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Text processing test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_alignment_engine():
    """Test the alignment engine (requires internet for model download)."""
    print("=" * 60)
    print("TEST 3: Alignment Engine")
    print("=" * 60)
    
    try:
        from src.models import load_strategies, load_actions
        from src.alignment import AlignmentEngine
        from src.recommendations import generate_recommendations
        
        print("📥 Loading data...")
        strategies = load_strategies('data/strategic.json')
        actions = load_actions('data/action.json')
        
        print("🤖 Initializing alignment engine...")
        print("   (This may take a moment to download the model on first run)")
        engine = AlignmentEngine()
        
        print("🔍 Analyzing alignment...")
        results = engine.analyze_alignment(strategies, actions, top_k=5)
        
        print(f"\n📊 Results:")
        print(f"   Overall Synchronization Score: {results['overall_synchronization_score']:.2f}%")
        print(f"   Coverage: {results['coverage_percentage']:.2f}%")
        print(f"   Total Strategies: {results['total_strategies']}")
        print(f"   Total Actions: {results['total_actions']}")
        
        print(f"\n📋 Strategy-wise alignment:")
        for s in results['strategy_alignments']:
            print(f"   • {s['strategy_title'][:40]:40} | Score: {s['average_score']:.3f} | {s['alignment_level']}")
        
        print("\n💡 Generating recommendations...")
        recommendations = generate_recommendations(results, strategies)
        print(f"   Generated {len(recommendations)} recommendation sets")
        
        # Save results
        outputs_dir = Path('outputs')
        outputs_dir.mkdir(exist_ok=True)
        output_file = outputs_dir / 'test_results.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'results': results,
                'recommendations': recommendations
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        assert results['overall_synchronization_score'] >= 0, "Invalid sync score"
        assert results['overall_synchronization_score'] <= 100, "Sync score out of range"
        
        print("\n✅ Alignment engine test PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Alignment engine test FAILED: {e}")
        print("\nNote: This test requires internet connection to download the ML model.")
        print("If you see a connection error, the code is correct but the model")
        print("couldn't be downloaded. Try running this test with internet access.\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print(" Strategy-Action Synchronization AI - Test Suite")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Data Loading", test_data_loading()))
    results.append(("Text Processing", test_text_processing()))
    results.append(("Alignment Engine", test_alignment_engine()))
    
    # Summary
    print("\n" + "=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
