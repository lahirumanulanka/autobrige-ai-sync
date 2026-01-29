"""
Intelligent recommendation system for improving strategy-action alignment.
"""

from typing import List, Dict, Any
from src.models import StrategicObjective


def generate_recommendations(
    alignment_results: Dict[str, Any],
    strategies: List[StrategicObjective]
) -> List[Dict[str, Any]]:
    """
    Generate intelligent recommendations based on alignment analysis.
    
    Args:
        alignment_results: Results from AlignmentEngine.analyze_alignment()
        strategies: Original list of strategic objectives
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Create a mapping of strategy IDs to strategy objects
    strategy_map = {s.id: s for s in strategies}
    
    for strategy_alignment in alignment_results['strategy_alignments']:
        strategy_id = strategy_alignment['strategy_id']
        strategy_title = strategy_alignment['strategy_title']
        alignment_level = strategy_alignment['alignment_level']
        average_score = strategy_alignment['average_score']
        matching_actions = strategy_alignment['matching_actions']
        
        strategy_obj = strategy_map.get(strategy_id)
        
        recommendation = {
            'strategy_id': strategy_id,
            'strategy_title': strategy_title,
            'alignment_level': alignment_level,
            'recommendations': []
        }
        
        # Generate recommendations based on alignment level
        if alignment_level == "Weak":
            # For weak alignment, suggest comprehensive improvements
            recommendation['recommendations'].extend([
                {
                    'type': 'Critical',
                    'category': 'Action Gap',
                    'message': f"This strategic objective has weak alignment (score: {average_score:.2f}). Immediate action is required."
                },
                {
                    'type': 'Action Required',
                    'category': 'Missing Actions',
                    'message': f"Define new action tasks that directly address '{strategy_title}'. Consider breaking down the objective into specific, measurable activities."
                },
                {
                    'type': 'Planning',
                    'category': 'Resource Allocation',
                    'message': "Assign clear ownership, timelines, and resources to new actions. Ensure each action has a responsible owner and deadline."
                }
            ])
            
            # If strategy has KPIs, suggest KPI-aligned actions
            if strategy_obj and strategy_obj.kpis:
                recommendation['recommendations'].append({
                    'type': 'Performance',
                    'category': 'KPI Alignment',
                    'message': f"Create actions that directly contribute to measuring and achieving the defined KPIs: {', '.join(strategy_obj.kpis[:2])}{'...' if len(strategy_obj.kpis) > 2 else ''}."
                })
            else:
                recommendation['recommendations'].append({
                    'type': 'Performance',
                    'category': 'KPI Definition',
                    'message': "Define measurable KPIs for this strategic objective to track progress effectively."
                })
        
        elif alignment_level == "Medium":
            # For medium alignment, suggest strengthening
            recommendation['recommendations'].extend([
                {
                    'type': 'Improvement',
                    'category': 'Strengthen Alignment',
                    'message': f"This objective has moderate alignment (score: {average_score:.2f}). Consider refining existing actions or adding complementary ones."
                },
                {
                    'type': 'Review',
                    'category': 'Action Refinement',
                    'message': "Review current action plans to ensure they explicitly address the strategic objective. Add specific deliverables that demonstrate strategic impact."
                }
            ])
            
            # Check if there are any weak matching actions
            weak_matches = [m for m in matching_actions if m['alignment'] == 'Weak']
            if weak_matches:
                recommendation['recommendations'].append({
                    'type': 'Optimization',
                    'category': 'Replace Weak Actions',
                    'message': f"{len(weak_matches)} of the matched actions have weak alignment. Consider replacing or restructuring them for better strategic fit."
                })
            
            # Suggest monitoring
            recommendation['recommendations'].append({
                'type': 'Monitoring',
                'category': 'Track Progress',
                'message': "Establish regular review cycles to monitor whether actions are effectively contributing to the strategic objective."
            })
        
        else:  # Strong alignment
            # For strong alignment, focus on monitoring and optimization
            recommendation['recommendations'].extend([
                {
                    'type': 'Success',
                    'category': 'Strong Alignment',
                    'message': f"Excellent alignment detected (score: {average_score:.2f}). Current actions are well-aligned with this strategic objective."
                },
                {
                    'type': 'Monitoring',
                    'category': 'Continuous Review',
                    'message': "Maintain regular reviews to ensure continued alignment as actions progress and circumstances change."
                }
            ])
            
            # Check if priority is high
            if strategy_obj and strategy_obj.priority.lower() == 'high':
                recommendation['recommendations'].append({
                    'type': 'Priority',
                    'category': 'High Priority Focus',
                    'message': "As a high-priority objective, ensure adequate resources and executive attention are maintained throughout execution."
                })
            
            # Suggest documentation
            recommendation['recommendations'].append({
                'type': 'Best Practice',
                'category': 'Document Success',
                'message': "Document the approach and learnings from this well-aligned strategy-action relationship as a template for other objectives."
            })
        
        recommendations.append(recommendation)
    
    # Add overall system recommendations
    overall_score = alignment_results['overall_synchronization_score']
    coverage = alignment_results['coverage_percentage']
    
    overall_recommendation = {
        'strategy_id': 'OVERALL',
        'strategy_title': 'Overall Synchronization',
        'alignment_level': 'Strong' if overall_score >= 60 else 'Medium' if overall_score >= 40 else 'Weak',
        'recommendations': []
    }
    
    if overall_score < 60:
        overall_recommendation['recommendations'].append({
            'type': 'Strategic',
            'category': 'System-Wide Gap',
            'message': f"Overall synchronization score is {overall_score:.1f}%. Focus on strengthening alignment across all strategic objectives."
        })
    
    if coverage < 70:
        overall_recommendation['recommendations'].append({
            'type': 'Coverage',
            'category': 'Action Coverage',
            'message': f"Only {coverage:.1f}% of strategies have adequate action coverage. Aim for at least 2 strong actions per strategic objective."
        })
    
    recommendations.append(overall_recommendation)
    
    return recommendations
