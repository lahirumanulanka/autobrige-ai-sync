"""
Streamlit Dashboard for Strategy-Action Synchronization AI
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import load_strategies, load_actions
from src.alignment import AlignmentEngine
from src.recommendations import generate_recommendations


# Page configuration
st.set_page_config(
    page_title="Strategy-Action Synchronization AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


def save_results(results, recommendations):
    """Save results to JSON file in outputs directory."""
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sync_analysis_{timestamp}.json"
    filepath = outputs_dir / filename
    
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "alignment_results": results,
        "recommendations": recommendations
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    return filepath


def main():
    # Title and description
    st.title("🎯 Strategy-Action Synchronization AI")
    st.markdown("""
    ### MSc Coursework Project: AutoBridge Import Platform
    
    This AI system analyzes the alignment between your **Strategic Plan** and **Action Plan** 
    using advanced embedding techniques and similarity analysis.
    
    **Features:**
    - Semantic matching using sentence transformers
    - Vector similarity search with ChromaDB
    - Intelligent recommendations for improvement
    - Downloadable JSON reports
    """)
    
    st.divider()
    
    # Sidebar for data input
    with st.sidebar:
        st.header("📊 Data Input")
        
        data_source = st.radio(
            "Choose data source:",
            ["Use Sample Data", "Upload JSON Files"],
            help="Sample data contains AutoBridge import platform strategies and actions"
        )
        
        strategies_path = None
        actions_path = None
        
        if data_source == "Use Sample Data":
            strategies_path = "data/strategic.json"
            actions_path = "data/action.json"
            st.success("✅ Using sample data from data/ folder")
        else:
            st.markdown("#### Upload Files")
            strategies_file = st.file_uploader(
                "Strategic Objectives JSON",
                type=['json'],
                help="Upload JSON file with strategic objectives"
            )
            actions_file = st.file_uploader(
                "Action Tasks JSON",
                type=['json'],
                help="Upload JSON file with action tasks"
            )
            
            if strategies_file and actions_file:
                # Save uploaded files temporarily
                with open("/tmp/strategies.json", "wb") as f:
                    f.write(strategies_file.getvalue())
                with open("/tmp/actions.json", "wb") as f:
                    f.write(actions_file.getvalue())
                
                strategies_path = "/tmp/strategies.json"
                actions_path = "/tmp/actions.json"
                st.success("✅ Files uploaded successfully")
        
        st.divider()
        
        # Analysis parameters
        st.header("⚙️ Parameters")
        top_k = st.slider(
            "Top K matching actions",
            min_value=3,
            max_value=10,
            value=5,
            help="Number of best matching actions to show per strategy"
        )
        
        st.divider()
        
        # Run button
        run_analysis = st.button(
            "🚀 Run Synchronization Analysis",
            type="primary",
            use_container_width=True,
            disabled=(strategies_path is None or actions_path is None)
        )
    
    # Main content area
    if run_analysis:
        try:
            with st.spinner("🔄 Loading data..."):
                # Load data
                strategies = load_strategies(strategies_path)
                actions = load_actions(actions_path)
                
                st.info(f"Loaded {len(strategies)} strategic objectives and {len(actions)} action tasks")
            
            with st.spinner("🤖 Analyzing alignment (this may take a minute)..."):
                # Try to initialize real alignment engine, fall back to demo if needed
                try:
                    from src.alignment import AlignmentEngine
                    engine = AlignmentEngine()
                    using_demo = False
                except Exception as e:
                    st.warning("⚠️ Using demo mode (sentence transformer model not available). Results are simulated for demonstration.")
                    from src.demo_alignment import DemoAlignmentEngine
                    engine = DemoAlignmentEngine()
                    using_demo = True
                
                # Perform analysis
                results = engine.analyze_alignment(strategies, actions, top_k=top_k)
                
                # Generate recommendations
                recommendations = generate_recommendations(results, strategies)
            
            st.success("✅ Analysis completed successfully!")
            
            # Display overall metrics
            st.header("📈 Overall Synchronization Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                score = results['overall_synchronization_score']
                st.metric(
                    "Synchronization Score",
                    f"{score:.1f}%",
                    delta=None,
                    help="Average alignment score across all strategies (0-100)"
                )
            
            with col2:
                coverage = results['coverage_percentage']
                st.metric(
                    "Coverage",
                    f"{coverage:.1f}%",
                    delta=None,
                    help="Percentage of strategies with ≥2 strong actions"
                )
            
            with col3:
                st.metric(
                    "Strategies",
                    results['total_strategies'],
                    delta=None,
                    help="Total strategic objectives analyzed"
                )
            
            with col4:
                st.metric(
                    "Actions",
                    results['total_actions'],
                    delta=None,
                    help="Total action tasks in the plan"
                )
            
            # Overall status indicator
            if score >= 60:
                st.success("🎉 **Strong overall synchronization** - Strategic plan is well-aligned with actions!")
            elif score >= 40:
                st.warning("⚠️ **Medium synchronization** - Some improvements recommended to strengthen alignment.")
            else:
                st.error("🚨 **Weak synchronization** - Significant gaps detected. Immediate action required.")
            
            st.divider()
            
            # Strategy-wise alignment table
            st.header("📋 Strategy-Wise Alignment Summary")
            
            # Prepare data for table
            table_data = []
            for strategy_result in results['strategy_alignments']:
                table_data.append({
                    "Strategy": strategy_result['strategy_title'],
                    "Priority": strategy_result['strategy_priority'],
                    "Avg Score": f"{strategy_result['average_score']:.3f}",
                    "Alignment": strategy_result['alignment_level'],
                    "Top Actions": len(strategy_result['matching_actions'])
                })
            
            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True
            )
            
            st.divider()
            
            # Detailed strategy results
            st.header("🔍 Detailed Strategy Analysis")
            
            for strategy_result in results['strategy_alignments']:
                with st.expander(
                    f"**{strategy_result['strategy_title']}** - {strategy_result['alignment_level']} Alignment",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Priority", strategy_result['strategy_priority'])
                    with col2:
                        st.metric("Average Score", f"{strategy_result['average_score']:.3f}")
                    with col3:
                        st.metric("Alignment", strategy_result['alignment_level'])
                    
                    st.markdown("##### Matching Actions")
                    
                    for i, action in enumerate(strategy_result['matching_actions'], 1):
                        alignment_color = {
                            'Strong': '🟢',
                            'Medium': '🟡',
                            'Weak': '🔴'
                        }.get(action['alignment'], '⚪')
                        
                        st.markdown(
                            f"{alignment_color} **{i}. {action['action_title']}** "
                            f"(Score: {action['similarity_score']:.3f}, {action['alignment']})"
                        )
            
            st.divider()
            
            # Recommendations
            st.header("💡 Intelligent Recommendations")
            
            for rec in recommendations:
                if rec['strategy_id'] == 'OVERALL':
                    st.subheader("🌐 System-Wide Recommendations")
                else:
                    st.subheader(f"📌 {rec['strategy_title']}")
                
                alignment_badge = {
                    'Strong': '🟢 Strong',
                    'Medium': '🟡 Medium',
                    'Weak': '🔴 Weak'
                }.get(rec['alignment_level'], rec['alignment_level'])
                
                st.markdown(f"**Alignment Level:** {alignment_badge}")
                
                for item in rec['recommendations']:
                    with st.container():
                        st.markdown(f"**{item['type']}** - *{item['category']}*")
                        st.info(item['message'])
                
                st.divider()
            
            # Save and download results
            st.header("💾 Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Save Results to outputs/", use_container_width=True):
                    filepath = save_results(results, recommendations)
                    st.success(f"✅ Results saved to: {filepath}")
            
            with col2:
                # Prepare download data
                download_data = {
                    "timestamp": datetime.now().isoformat(),
                    "alignment_results": results,
                    "recommendations": recommendations
                }
                
                st.download_button(
                    label="📥 Download as JSON",
                    data=json.dumps(download_data, indent=2, ensure_ascii=False),
                    file_name=f"sync_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.exception(e)
    
    else:
        # Show instructions when not running
        st.info("""
        👈 **Get Started:**
        1. Select your data source in the sidebar
        2. Adjust parameters if needed
        3. Click "Run Synchronization Analysis"
        
        The system will analyze alignment between your strategic objectives and action tasks, 
        providing detailed insights and recommendations.
        """)
        
        # Show sample data preview
        if os.path.exists("data/strategic.json") and os.path.exists("data/action.json"):
            with st.expander("📄 Preview Sample Data"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Strategic Objectives Sample")
                    with open("data/strategic.json", 'r') as f:
                        strategies_sample = json.load(f)
                    st.json(strategies_sample[0] if strategies_sample else {})
                
                with col2:
                    st.markdown("##### Action Tasks Sample")
                    with open("data/action.json", 'r') as f:
                        actions_sample = json.load(f)
                    st.json(actions_sample[0] if actions_sample else {})


if __name__ == "__main__":
    main()
