# Quick Start Guide

## 5-Minute Setup

Get the Strategy-Action Synchronization AI system running in 5 minutes!

### Step 1: Install (2 minutes)

```bash
# Clone and enter directory
git clone <repo-url>
cd autobrige-ai-sync

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (this may take 1-2 minutes)
pip install -r requirements.txt
```

### Step 2: Run (30 seconds)

```bash
streamlit run app/streamlit_app.py
```

Your browser will open to `http://localhost:8501`

### Step 3: Try It (2 minutes)

1. In the sidebar, keep "Sample Data" selected
2. Click the **"Run Synchronization"** button
3. Wait ~30 seconds for analysis
4. Explore the results!

That's it! 🎉

## What You'll See

### Overall Metrics
- **Synchronization Score**: How well actions align with strategies (0-100)
- **Coverage**: % of strategies with strong action support
- **Strategy Count**: 8 AutoBridge strategies
- **Action Count**: 38 AutoBridge actions

### Strategy Mapping
Table showing each strategy's:
- Alignment score
- Best matching action
- Strength (Strong/Medium/Weak)

### Detailed Analysis
For each strategy:
- Top 5 most similar actions with similarity scores
- Improvement recommendations
- Proposed new actions
- KPI suggestions
- Risk assessment

### Downloadable Outputs
- `alignment_results.json`: Full alignment data
- `recommendations.json`: All recommendations
- `eval_summary.csv`: Summary table

## Next Steps

### Try Your Own Data

1. Click "Upload Files" in sidebar
2. Upload your strategic.json and action.json files
3. Run analysis

**JSON Format**:

```json
// strategic.json
[
  {
    "id": "S001",
    "title": "Strategic Objective Title",
    "description": "What you want to achieve",
    "kpis": ["KPI 1", "KPI 2"],
    "priority": "High"
  }
]

// action.json
[
  {
    "id": "A001",
    "title": "Action Task Title",
    "description": "What you're doing",
    "owner": "Team Name",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "outputs": ["Deliverable 1"]
  }
]
```

### Enable AI Recommendations (Optional)

For LLM-powered suggestions:

```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Restart Streamlit
streamlit run app/streamlit_app.py
```

Check the "Enable RAG" box in the sidebar.

### Adjust Parameters

In the sidebar:
- **Top-K**: Number of actions to retrieve per strategy (3-10)
- **Recommendation Threshold**: Generate detailed suggestions below this score (0-1)

## Understanding Results

### Alignment Scores

- **0.75-1.0**: Strong alignment ✅
- **0.55-0.75**: Medium alignment ⚠️
- **0.0-0.55**: Weak alignment ❌

### What Strong Alignment Means

Actions and strategies use similar concepts, suggesting:
- Actions directly support the strategy
- Clear connection between what you plan and what you do
- Resources likely allocated effectively

### What Weak Alignment Means

Actions and strategies are semantically distant, suggesting:
- Strategy may lack supporting actions
- Actions may not target strategic goals
- Gap analysis needed

## Common Use Cases

### 1. Strategy Review
**Goal**: Validate strategic plan has action support

**How**:
1. Load current strategies and actions
2. Review overall score and coverage
3. Focus on weak strategies
4. Use recommendations to fill gaps

### 2. Action Prioritization
**Goal**: Identify which actions best support strategy

**How**:
1. Run analysis
2. Sort strategies by alignment score
3. Focus resources on high-alignment actions
4. Deprioritize low-alignment actions

### 3. Gap Analysis
**Goal**: Find strategies needing more actions

**How**:
1. Check "Weak Strategies" section
2. Review proposed new actions
3. Assess recommendations
4. Create action plan

### 4. Quarterly Planning
**Goal**: Ensure next quarter's actions align

**How**:
1. Load strategic plan
2. Upload proposed actions for next quarter
3. Validate alignment before committing
4. Adjust action portfolio based on results

## Tips & Tricks

### Getting Better Results

1. **Clear Descriptions**: Write detailed strategy/action descriptions
2. **Specific KPIs**: Include measurable KPIs in strategies
3. **Consistent Language**: Use similar terminology across strategies and actions
4. **Regular Reviews**: Run analysis quarterly to track alignment trends

### Interpreting Recommendations

- **Detailed recommendations**: Generated for weak-aligned strategies
- **Light suggestions**: Generated for well-aligned strategies
- **Rule-based (fallback)**: Generic but useful suggestions
- **LLM-powered (RAG)**: Contextual, specific recommendations

### Download Best Practices

- **alignment_results.json**: Keep for historical comparison
- **recommendations.json**: Share with team for action planning
- **eval_summary.csv**: Import to Excel/Google Sheets for reporting

## Troubleshooting

### "Error loading data"
- Check JSON files are valid arrays
- Verify all required fields present (id, title, description)

### "Model download stuck"
- First run downloads ~90MB model
- Requires internet connection
- May take 2-5 minutes

### "No results showing"
- Check browser console for errors
- Try refreshing the page
- Verify data files loaded correctly

### "Low alignment scores"
- May indicate genuine gap
- Or strategies/actions use very different language
- Review recommendations for improvement

## Advanced Usage

### Custom Models

Edit `src/embeddings.py` to use different model:

```python
self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
```

### Batch Processing

Process multiple strategy sets:

```python
from src.alignment import AlignmentEngine
from src.models import load_strategies, load_actions

for dataset in datasets:
    strategies = load_strategies(f'data/{dataset}/strategic.json')
    actions = load_actions(f'data/{dataset}/action.json')
    engine = AlignmentEngine(strategies, actions)
    results = engine.compute_alignment()
    # Save results
```

### API Integration

Build REST API on top:

```python
from fastapi import FastAPI
from src.alignment import AlignmentEngine

app = FastAPI()

@app.post("/analyze")
def analyze(strategies: List[dict], actions: List[dict]):
    # Process and return results
    pass
```

## Need Help?

- **Documentation**: See README.md for full details
- **Deployment**: See DEPLOYMENT.md for production setup
- **Issues**: Open GitHub issue
- **Questions**: Check FAQ section in README

## MSc Coursework Context

This system demonstrates:
- **Semantic Search**: Using embeddings for meaning-based matching
- **Vector Databases**: Efficient similarity search with ChromaDB
- **RAG (Retrieval-Augmented Generation)**: Grounding LLM outputs with retrieved context
- **Practical NLP**: Real-world application of transformer models

Perfect for demonstrating understanding of modern NLP and AI systems!

---

**Ready to explore?** Run `streamlit run app/streamlit_app.py` and start analyzing! 🚀
