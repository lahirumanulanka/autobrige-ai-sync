"""
Streamlit application for Strategy-Action Synchronization AI System
"""
import streamlit as st
import json
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import load_strategies, load_actions
from src.alignment import AlignmentEngine
from src.recommendations import generate_recommendations
from src.evaluation import export_evaluation_summary, generate_evaluation_report
from src.llm_client import is_llm_available


# Page configuration
st.set_page_config(
    page_title="Strategy-Action Synchronization AI",
    page_icon="🎯",
    layout="wide"
)

# Title and description
st.title("🎯 Strategy-Action Synchronization AI")
st.markdown("""
This RAG-based system analyzes alignment between strategic objectives and action tasks,
providing AI-powered recommendations for improvement.
""")

# Sidebar configuration
st.sidebar.header("Configuration")

# Data source selection
data_source = st.sidebar.radio(
    "Data Source",
    ["Sample Data", "Upload Files"]
)

strategic_path = None
action_path = None

if data_source == "Sample Data":
    strategic_path = "data/strategic.json"
    action_path = "data/action.json"
    st.sidebar.success("Using sample AutoBridge data")
else:
    st.sidebar.subheader("Upload JSON Files")
    strategic_file = st.sidebar.file_uploader(
        "Strategic Objectives (JSON)",
        type=["json"],
        key="strategic"
    )
    action_file = st.sidebar.file_uploader(
        "Action Tasks (JSON)",
        type=["json"],
        key="actions"
    )
    
    if strategic_file and action_file:
        # Save uploaded files temporarily
        os.makedirs("outputs/temp", exist_ok=True)
        strategic_path = "outputs/temp/strategic.json"
        action_path = "outputs/temp/action.json"
        
        with open(strategic_path, "wb") as f:
            f.write(strategic_file.getvalue())
        with open(action_path, "wb") as f:
            f.write(action_file.getvalue())

# Parameters
st.sidebar.subheader("Parameters")
top_k = st.sidebar.slider(
    "Top-K Actions per Strategy",
    min_value=3,
    max_value=10,
    value=5,
    help="Number of most similar actions to retrieve for each strategy"
)

# RAG settings
llm_available = is_llm_available()
st.sidebar.subheader("RAG Settings")

if llm_available:
    st.sidebar.success("✅ LLM API Key detected")
    rag_enabled = st.sidebar.checkbox(
        "Enable RAG (LLM-powered suggestions)",
        value=True,
        help="Use OpenAI LLM for generating improvement suggestions"
    )
else:
    st.sidebar.warning("⚠️ No LLM API Key found")
    st.sidebar.info("System will run in fallback mode with rule-based suggestions")
    rag_enabled = False

# Recommendation threshold
rec_threshold = st.sidebar.slider(
    "Recommendation Threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.60,
    step=0.05,
    help="Strategies below this similarity score get detailed recommendations"
)

# Run button
run_button = st.sidebar.button("🚀 Run Synchronization", type="primary", use_container_width=True)

# Main content
if run_button:
    if not strategic_path or not action_path:
        st.error("Please select or upload both strategic objectives and action tasks files.")
    else:
        try:
            # Load data
            with st.spinner("Loading data..."):
                strategies = load_strategies(strategic_path)
                actions = load_actions(action_path)
                
                st.success(f"Loaded {len(strategies)} strategies and {len(actions)} actions")
            
            # Run alignment
            with st.spinner("Computing alignment..."):
                engine = AlignmentEngine(strategies, actions)
                alignment_results = engine.compute_alignment(top_k=top_k)
                
                # Save alignment results
                os.makedirs("outputs", exist_ok=True)
                with open("outputs/alignment_results.json", "w") as f:
                    json.dump(alignment_results, f, indent=2)
            
            # Generate recommendations
            with st.spinner("Generating recommendations..."):
                recommendations = generate_recommendations(
                    strategies=strategies,
                    alignment_result=alignment_results,
                    rag_enabled=rag_enabled,
                    threshold=rec_threshold
                )
                
                # Save recommendations
                with open("outputs/recommendations.json", "w") as f:
                    json.dump(recommendations, f, indent=2)
            
            # Generate evaluation report
            with st.spinner("Computing evaluation metrics..."):
                eval_report = generate_evaluation_report(alignment_results)
                eval_df = export_evaluation_summary(alignment_results, "outputs/eval_summary.csv")
            
            st.success("✅ Analysis complete!")
            
            # Display results
            st.header("📊 Overall Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Synchronization Score",
                    f"{alignment_results['overall_score']:.1f}/100",
                    help="Average alignment score across all strategies"
                )
            
            with col2:
                st.metric(
                    "Coverage",
                    f"{alignment_results['coverage_pct']:.1f}%",
                    help="% of strategies with ≥2 strong matches"
                )
            
            with col3:
                st.metric(
                    "Strategies",
                    alignment_results['strategy_count']
                )
            
            with col4:
                st.metric(
                    "Actions",
                    alignment_results['action_count']
                )
            
            # Strategy mapping table
            st.header("📋 Strategy-Action Mapping")
            
            # Build table data
            table_data = []
            for strategy in alignment_results['strategy_mapping']:
                top_action = strategy['retrieved_actions'][0] if strategy['retrieved_actions'] else None
                table_data.append({
                    'Strategy ID': strategy['strategy_id'],
                    'Strategy Title': strategy['strategy_title'],
                    'Avg Similarity': f"{strategy['avg_top3_similarity']:.3f}",
                    'Best Action': top_action['metadata']['title'] if top_action else 'N/A',
                    'Strength': 'Strong' if strategy['avg_top3_similarity'] >= 0.75 
                               else 'Medium' if strategy['avg_top3_similarity'] >= 0.55 
                               else 'Weak'
                })
            
            st.dataframe(table_data, use_container_width=True)
            
            # Detailed strategy analysis
            st.header("🔍 Detailed Analysis")
            
            for i, strategy in enumerate(alignment_results['strategy_mapping']):
                with st.expander(f"**{strategy['strategy_title']}** (Score: {strategy['avg_top3_similarity']:.3f})"):
                    # Strategy info
                    st.subheader("Strategy Details")
                    st.write(f"**ID:** {strategy['strategy_id']}")
                    st.write(f"**Alignment Score:** {strategy['avg_top3_similarity']:.3f}")
                    st.write(f"**Strong Matches:** {strategy['strong_match_count']}")
                    
                    # Retrieved actions
                    st.subheader("Retrieved Actions")
                    for j, action in enumerate(strategy['retrieved_actions'][:5], 1):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"{j}. **{action['metadata']['title']}**")
                            st.caption(f"Owner: {action['metadata']['owner']}")
                        with col2:
                            st.write(f"Similarity: {action['similarity']:.3f}")
                        with col3:
                            strength_color = {
                                'Strong': '🟢',
                                'Medium': '🟡',
                                'Weak': '🔴'
                            }
                            st.write(f"{strength_color[action['strength']]} {action['strength']}")
                    
                    # Recommendations
                    st.subheader("💡 Recommendations")
                    rec = recommendations[i]
                    
                    if rec.get('llm_enabled'):
                        st.info("🤖 Generated using LLM")
                    else:
                        st.info("📋 Rule-based suggestions (fallback mode)")
                    
                    # Show augmented prompt preview if detailed
                    if rec['recommendation_type'] == 'detailed':
                        with st.expander("View Augmented Prompt Preview"):
                            st.code(rec['augmented_prompt_preview'], language="text")
                    
                    # Suggestions
                    st.write("**Improvement Suggestions:**")
                    for suggestion in rec['suggestions']:
                        st.write(f"• {suggestion}")
                    
                    # KPIs
                    if rec.get('kpis'):
                        st.write("**Recommended KPIs:**")
                        for kpi in rec['kpis']:
                            st.write(f"• {kpi}")
                    
                    # Risks
                    if rec.get('risks'):
                        st.write("**Risk Assessment:**")
                        for risk in rec['risks']:
                            st.write(f"⚠️ {risk}")
                    
                    # New actions
                    if rec.get('new_actions'):
                        st.write("**Proposed New Actions:**")
                        for new_action in rec['new_actions']:
                            st.write(f"**{new_action['title']}**")
                            st.write(f"- Description: {new_action['description']}")
                            st.write(f"- Owner: {new_action['owner']}")
                            st.write(f"- Timeline: {new_action['timeline']}")
            
            # Download section
            st.header("📥 Download Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                with open("outputs/alignment_results.json", "r") as f:
                    st.download_button(
                        "Download Alignment Results",
                        data=f.read(),
                        file_name="alignment_results.json",
                        mime="application/json"
                    )
            
            with col2:
                with open("outputs/recommendations.json", "r") as f:
                    st.download_button(
                        "Download Recommendations",
                        data=f.read(),
                        file_name="recommendations.json",
                        mime="application/json"
                    )
            
            with col3:
                with open("outputs/eval_summary.csv", "r") as f:
                    st.download_button(
                        "Download Evaluation Summary",
                        data=f.read(),
                        file_name="eval_summary.csv",
                        mime="text/csv"
                    )
            
            # Evaluation metrics
            st.header("📈 Evaluation Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Coverage Metrics")
                coverage = eval_report['coverage_metrics']
                st.write(f"**Strong Alignment:** {coverage['strong_alignment_count']} strategies ({coverage['strong_alignment_pct']:.1f}%)")
                st.write(f"**Medium Alignment:** {coverage['medium_alignment_count']} strategies ({coverage['medium_alignment_pct']:.1f}%)")
                st.write(f"**Weak Alignment:** {coverage['weak_alignment_count']} strategies ({coverage['weak_alignment_pct']:.1f}%)")
            
            with col2:
                st.subheader("Similarity Distribution")
                dist = eval_report['distribution_metrics']
                st.write(f"**Mean:** {dist['mean']:.3f}")
                st.write(f"**Median:** {dist['median']:.3f}")
                st.write(f"**Std Dev:** {dist['std']:.3f}")
                st.write(f"**Range:** {dist['min']:.3f} - {dist['max']:.3f}")
            
            # Weak strategies warning
            if alignment_results['weak_strategies']:
                st.warning(f"⚠️ **{len(alignment_results['weak_strategies'])} strategies** have weak alignment (score < 0.55)")
                for weak in alignment_results['weak_strategies']:
                    st.write(f"• {weak['title']} (score: {weak['avg_top3_similarity']:.3f})")
        
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            st.exception(e)

else:
    # Initial instructions
    st.info("👈 Configure settings in the sidebar and click 'Run Synchronization' to begin analysis")
    
    st.markdown("""
    ### How to Use
    
    1. **Choose Data Source**: Use sample data or upload your own JSON files
    2. **Adjust Parameters**: Set top-k value and recommendation threshold
    3. **Configure RAG**: Enable LLM-powered suggestions if API key is available
    4. **Run Analysis**: Click the 'Run Synchronization' button
    5. **Review Results**: Explore alignment scores, recommendations, and metrics
    6. **Download**: Export results as JSON and CSV files
    
    ### System Architecture
    
    ```
    Strategic Plan + Action Plan
    ↓
    Text Embeddings (SentenceTransformers)
    ↓
    Vector Database (ChromaDB)
    ↓
    Context Retrieval (Top-K)
    ↓
    Prompt Augmentation (RAG)
    ↓
    LLM Generation (OpenAI) or Fallback
    ↓
    Improvement Suggestions
    ```
    
    ### Requirements
    
    - **Strategic Objectives JSON**: Array of strategies with id, title, description, kpis, priority
    - **Action Tasks JSON**: Array of actions with id, title, description, owner, dates, outputs
    - **Optional LLM Key**: Set `OPENAI_API_KEY` in `.env` file for RAG generation
    """)
