"""
Evaluation metrics for strategy-action synchronization.
"""
import pandas as pd
from typing import Dict, Any, List


def compute_coverage_metrics(alignment_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute coverage metrics from alignment results.
    
    Args:
        alignment_result: Output from AlignmentEngine.compute_alignment()
        
    Returns:
        Dictionary of coverage metrics
    """
    strategy_mappings = alignment_result['strategy_mapping']
    
    # Count strategies by alignment strength
    strong_count = sum(1 for s in strategy_mappings if s['avg_top3_similarity'] >= 0.75)
    medium_count = sum(1 for s in strategy_mappings if 0.55 <= s['avg_top3_similarity'] < 0.75)
    weak_count = sum(1 for s in strategy_mappings if s['avg_top3_similarity'] < 0.55)
    
    total_strategies = len(strategy_mappings)
    
    return {
        'total_strategies': total_strategies,
        'strong_alignment_count': strong_count,
        'medium_alignment_count': medium_count,
        'weak_alignment_count': weak_count,
        'strong_alignment_pct': round(strong_count / total_strategies * 100, 2) if total_strategies > 0 else 0,
        'medium_alignment_pct': round(medium_count / total_strategies * 100, 2) if total_strategies > 0 else 0,
        'weak_alignment_pct': round(weak_count / total_strategies * 100, 2) if total_strategies > 0 else 0,
        'coverage_pct': alignment_result['coverage_pct'],
        'overall_score': alignment_result['overall_score']
    }


def compute_similarity_distribution(alignment_result: Dict[str, Any]) -> Dict[str, float]:
    """
    Compute statistical distribution of similarity scores.
    
    Args:
        alignment_result: Output from AlignmentEngine.compute_alignment()
        
    Returns:
        Dictionary of distribution statistics
    """
    strategy_mappings = alignment_result['strategy_mapping']
    similarities = [s['avg_top3_similarity'] for s in strategy_mappings]
    
    if not similarities:
        return {
            'mean': 0.0,
            'median': 0.0,
            'min': 0.0,
            'max': 0.0,
            'std': 0.0
        }
    
    import numpy as np
    
    return {
        'mean': round(float(np.mean(similarities)), 3),
        'median': round(float(np.median(similarities)), 3),
        'min': round(float(np.min(similarities)), 3),
        'max': round(float(np.max(similarities)), 3),
        'std': round(float(np.std(similarities)), 3)
    }


def export_evaluation_summary(
    alignment_result: Dict[str, Any],
    output_path: str = "outputs/eval_summary.csv"
) -> pd.DataFrame:
    """
    Export evaluation summary as CSV table.
    
    Args:
        alignment_result: Output from AlignmentEngine.compute_alignment()
        output_path: Path to save CSV file
        
    Returns:
        DataFrame containing evaluation summary
    """
    strategy_mappings = alignment_result['strategy_mapping']
    
    # Build table rows
    rows = []
    for strategy in strategy_mappings:
        # Get top action
        top_action = strategy['retrieved_actions'][0] if strategy['retrieved_actions'] else None
        
        row = {
            'strategy_id': strategy['strategy_id'],
            'strategy_title': strategy['strategy_title'],
            'avg_top3_similarity': round(strategy['avg_top3_similarity'], 3),
            'alignment_strength': 'Strong' if strategy['avg_top3_similarity'] >= 0.75 
                                 else 'Medium' if strategy['avg_top3_similarity'] >= 0.55 
                                 else 'Weak',
            'strong_match_count': strategy['strong_match_count'],
            'top_action_id': top_action['id'] if top_action else 'N/A',
            'top_action_title': top_action['metadata']['title'] if top_action else 'N/A',
            'top_action_similarity': round(top_action['similarity'], 3) if top_action else 0.0
        }
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Add summary statistics at the end
    summary_row = {
        'strategy_id': 'SUMMARY',
        'strategy_title': 'Overall Statistics',
        'avg_top3_similarity': round(alignment_result['overall_score'] / 100, 3),
        'alignment_strength': f"{alignment_result['coverage_pct']:.1f}% Coverage",
        'strong_match_count': sum(s['strong_match_count'] for s in strategy_mappings),
        'top_action_id': f"{alignment_result['strategy_count']} strategies",
        'top_action_title': f"{alignment_result['action_count']} actions",
        'top_action_similarity': ''
    }
    
    df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    
    return df


def generate_evaluation_report(alignment_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive evaluation report.
    
    Args:
        alignment_result: Output from AlignmentEngine.compute_alignment()
        
    Returns:
        Dictionary containing all evaluation metrics
    """
    coverage_metrics = compute_coverage_metrics(alignment_result)
    distribution_metrics = compute_similarity_distribution(alignment_result)
    
    return {
        'coverage_metrics': coverage_metrics,
        'distribution_metrics': distribution_metrics,
        'overall_score': alignment_result['overall_score'],
        'weak_strategies': alignment_result['weak_strategies']
    }
